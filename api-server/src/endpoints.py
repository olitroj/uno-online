from typing import Any
from fastapi import Body, Form, Depends, HTTPException, Request, Response
from hashlib import sha256
from asyncpg import UniqueViolationError
from main import app
from .db import db_query_one, db_query, db_execute
from .auth import generate_jwt, validate_jwt, JWT_NAME
from .schemas import AccountStatus

def get_current_user(req: Request) -> str:
    try:
        return validate_jwt(req.cookies.get(JWT_NAME))
    except:
        raise HTTPException(401)


def get_page_offset(page: int) -> int:
    if page < 0:
        raise HTTPException(400, "Page must be greater than or equal to 0")
    return page * 20

@app.post("/me")
async def post_me(username: str = Form(), password: str = Form()):
    password_hash = sha256(password.encode()).hexdigest()
    try:
        account_id = await db_query_one("INSERT INTO Accounts (username, password_hash) VALUES ($1, $2) RETURNING account_id;", username, password_hash)
    except UniqueViolationError:
        raise HTTPException(409, "Conflicting username")
    token = generate_jwt(str(account_id.get("account_id")))
    res = Response(status_code=201)
    res.set_cookie(key=JWT_NAME, value=token, httponly=True)
    return res


@app.delete("/me")
async def delete_me(account_id: str = Depends(get_current_user)):
    await db_execute("DELETE FROM Accounts WHERE account_id=$1;", account_id)
    res = Response(status_code=204)
    res.delete_cookie(JWT_NAME)
    return res


@app.put("/me")
async def put_me(data: Any = Body(), account_id: str = Depends(get_current_user)):
    if not isinstance(data, dict):
        raise HTTPException(400, "Request body must be an object")

    allowed_fields = {"username", "password", "status", "description"}
    if any(field not in allowed_fields for field in data):
        raise HTTPException(400, "Unexpected account field")

    values = []
    assignments = []

    if "username" in data:
        if not isinstance(data.get("username"), str):
            raise HTTPException(400, "Username must be a string")
        values.append(data.get("username"))
        assignments.append(f"username=${len(values)}")
    if "password" in data:
        if not isinstance(data.get("password"), str):
            raise HTTPException(400, "Password must be a string")
        password_hash = sha256(data.get("password").encode()).hexdigest()
        values.append(password_hash)
        assignments.append(f"password_hash=${len(values)}")
    if "status" in data:
        if not isinstance(data.get("status"), str) or data.get("status") not in [status.value for status in AccountStatus]:
            raise HTTPException(400, "Status must be 'online', 'offline' or 'ingame'")
        values.append(data.get("status"))
        assignments.append(f"status=${len(values)}")
    if "description" in data:
        if data.get("description") is not None and not isinstance(data.get("description"), str):
            raise HTTPException(400, "Description must be a string or null")
        values.append(data.get("description"))
        assignments.append(f"description=${len(values)}")

    if not assignments:
        return Response(status_code=200)

    values.append(account_id)
    try:
        await db_execute(
            f"UPDATE Accounts SET {', '.join(assignments)} WHERE account_id=${len(values)};",
            *values,
        )
    except UniqueViolationError:
        raise HTTPException(409, "Conflicting username")
    return Response(status_code=200)


@app.post("/me/token")
async def post_me_token(username: str = Form(), password: str = Form()):
    password_hash = sha256(password.encode()).hexdigest()
    account_id = await db_query_one(
        "SELECT account_id FROM Accounts WHERE username=$1 AND password_hash=$2;",
        username,
        password_hash,
    )
    if account_id is None:
        raise HTTPException(401)
    token = generate_jwt(str(account_id.get("account_id")))
    res = Response(status_code=200)
    res.set_cookie(key=JWT_NAME, value=token, httponly=True)
    return res


@app.delete("/me/token")
async def delete_me_token():
    res = Response(status_code=204)
    res.delete_cookie(key=JWT_NAME)
    return res


"""
    Potential query
    SELECT
        a.username,
        a.status,
        a.description,
        COUNT(p.game_id) FILTER (WHERE p.win = TRUE) AS wins,
        COALESCE(SUM(p.score), 0) AS total_score
    FROM Accounts a
    LEFT JOIN Participants p
        ON a.account_id = p.account_id
    WHERE a.account_id = $1
    GROUP BY a.account_id, a.username, a.status, a.description;
"""


@app.get("/me/info")
async def get_me_info(account_id: str = Depends(get_current_user)):
    return await get_account_info_by_id(account_id)


async def get_account_info_by_id(account_id: str):
    return await db_query_one(
        """
        SELECT
            a.username,
            a.status,
            a.description,
            COUNT(p.game_id) FILTER (WHERE p.win = TRUE) AS wins,
            COUNT(p.game_id) FILTER (WHERE p.win = FALSE) AS losses,
            COALESCE(SUM(p.score), 0) AS total_score
        FROM Accounts a
        LEFT JOIN Participants p
            ON a.account_id = p.account_id
        WHERE a.account_id = $1
        GROUP BY a.account_id, a.username, a.status, a.description;
    """,
        account_id,
    )


async def get_account_games_by_id(account_id: str, page: int = 0):
    return await db_query(
        """
        SELECT
            g.start_time,
            g.end_time,
            p.score,
            p.win
        FROM Participants p
        JOIN Games g
            ON g.game_id = p.game_id
        WHERE p.account_id = $1
        ORDER BY g.start_time DESC
        LIMIT 20 OFFSET $2;
        """,
        account_id,
        get_page_offset(page),
    )


@app.get("/me/games")
async def get_me_games(page: int = 0, account_id: str = Depends(get_current_user)):
    return await get_account_games_by_id(account_id, page)


@app.get("/me/friends")
async def get_me_friends(page: int = 0, account_id: str = Depends(get_current_user)):
    return await db_query(
        """
        SELECT
            a.username,
            f.status
        FROM Friends f
        JOIN Accounts a
            ON a.account_id = CASE
                WHEN f.account_id1 = $1 THEN f.account_id2
                ELSE f.account_id1
            END
        WHERE f.account_id1 = $1 OR f.account_id2 = $1
        ORDER BY a.username
        LIMIT 20 OFFSET $2;
        """,
        account_id,
        get_page_offset(page),
    )


async def get_account_id_by_username(username: str):
    account = await db_query_one(
        "SELECT account_id FROM Accounts WHERE username=$1;", username
    )
    if account is None:
        raise HTTPException(404)
    return str(account.get("account_id"))


async def ensure_can_view_account(current_account_id: str, account_id: str):
    if current_account_id == account_id:
        return
    friend = await db_query_one(
        """
        SELECT status FROM Friends
        WHERE account_id1=$1 AND account_id2=$2 AND status='accepted';
    """,
        min(current_account_id, account_id),
        max(current_account_id, account_id),
    )
    if friend is None:
        raise HTTPException(403)


@app.get("/account/info/{username}")
async def get_account_info(
    username: str, current_account_id: str = Depends(get_current_user)
):
    account_id = await get_account_id_by_username(username)
    await ensure_can_view_account(current_account_id, account_id)
    return await get_account_info_by_id(account_id)


@app.get("/account/games/{username}")
async def get_account_games(
    username: str, page: int = 0, current_account_id: str = Depends(get_current_user)
):
    account_id = await get_account_id_by_username(username)
    await ensure_can_view_account(current_account_id, account_id)
    return await get_account_games_by_id(account_id, page)


@app.post("/me/friends/{username}")
async def post_me_friends(
    username: str, current_account_id: str = Depends(get_current_user)
):
    account_id = await get_account_id_by_username(username)
    if account_id == current_account_id:
        raise HTTPException(404)
    account_id1 = account_id
    account_id2 = current_account_id
    if current_account_id < account_id:
        account_id1 = current_account_id
        account_id2 = account_id
    try:
        await db_execute(
            "INSERT INTO Friends (account_id1, account_id2) VALUES ($1, $2);",
            account_id1,
            account_id2,
        )
    except:
        raise HTTPException(404)
    return Response(status_code=201)


@app.patch("/me/friends/{username}")
async def patch_me_friends(
    username: str,
    action: str = Form(),
    current_account_id: str = Depends(get_current_user),
):
    if action != "accept" and action != "reject":
        raise HTTPException(400, "Action must be 'accept' or 'reject'")
    account_id = await get_account_id_by_username(username)
    account_id1 = account_id
    account_id2 = current_account_id
    if current_account_id < account_id:
        account_id1 = current_account_id
        account_id2 = account_id
    friend = await db_query_one(
        "SELECT status FROM Friends WHERE account_id1=$1 AND account_id2=$2;",
        account_id1,
        account_id2,
    )
    if friend is None:
        raise HTTPException(404)
    status = "accepted"
    if action == "reject":
        status = "rejected"
    await db_execute(
        "UPDATE Friends SET status=$1 WHERE account_id1=$2 AND account_id2=$3;",
        status,
        account_id1,
        account_id2,
    )
    return Response(status_code=200)


@app.delete("/me/friends/{username}")
async def delete_me_friends(
    username: str, current_account_id: str = Depends(get_current_user)
):
    account_id = await get_account_id_by_username(username)
    account_id1 = account_id
    account_id2 = current_account_id
    if current_account_id < account_id:
        account_id1 = current_account_id
        account_id2 = account_id
    friend = await db_query_one(
        "SELECT status FROM Friends WHERE account_id1=$1 AND account_id2=$2;",
        account_id1,
        account_id2,
    )
    if friend is None:
        raise HTTPException(404)
    await db_execute(
        "DELETE FROM Friends WHERE account_id1=$1 AND account_id2=$2;",
        account_id1,
        account_id2,
    )
    return Response(status_code=204)

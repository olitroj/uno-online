from fastapi import Form, Depends, HTTPException, Response
from hashlib import sha256
from asyncpg import UniqueViolationError
from main import app
from .db import db_query_one, db_query, db_execute
from .auth import generate_jwt, get_current_user, JWT_NAME


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
    pass


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
        page * 20,
    )


@app.post("/me/friends/{account_id}")
async def post_me_friends(
    account_id: str, current_account_id: str = Depends(get_current_user)
):
    friend = await db_query_one(
        "SELECT account_id FROM Accounts WHERE account_id=$1;", account_id
    )
    if friend is None or account_id == current_account_id:
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


@app.patch("/me/friends/{account_id}")
async def patch_me_friends(
    account_id: str, action: str = Form(), current_account_id: str = Depends(get_current_user)
):
    if action != "accept" and action != "reject":
        raise HTTPException(400, "Action must be 'accept' or 'reject'")
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


@app.delete("/me/friends/{account_id}")
async def delete_me_friends(
    account_id: str, current_account_id: str = Depends(get_current_user)
):
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

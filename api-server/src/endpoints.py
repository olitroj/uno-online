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
    account_id = await db_query_one("SELECT account_id FROM Accounts WHERE username=$1 AND password_hash=$2;", username, password_hash)
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


'''
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
'''
@app.get("/me/info")
async def get_me_info(account_id: str = Depends(get_current_user)):
    pass
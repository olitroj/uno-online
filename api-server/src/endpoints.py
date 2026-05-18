from fastapi import Form, Depends, HTTPException, Response

from main import app
from .db import db_query_one, db_query, db_execute
from .auth import generate_jwt, get_current_user
from .schemas import Account, Statistic

@app.post("/token")
async def post_token(username: str = Form(), password: str = Form()):
    existing_user = await db_query_one(Account, "SELECT * FROM Accounts WHERE username=$1 AND password=$2;", username, password)
    if existing_user is None:
        raise HTTPException(401)
    res = Response(status_code=201)
    res.set_cookie(key="access_token", value=generate_jwt(username), httponly=True)
    return res

@app.delete("/token")
async def delete_token():
    res = Response(status_code=204)
    res.delete_cookie("access_token")
    return res


@app.post("/account")
async def post_account(res: Response, username: str = Form(...), password: str = Form(...)):
    existing_user = await db_query_one(Account, "SELECT * FROM Accounts WHERE username=$1;", username)
    if existing_user is not None:
        raise HTTPException(409)
    await db_execute("INSERT INTO Accounts VALUES ($1, $2);", username, password)
    await db_execute("INSERT INTO Statistics (account_username) VALUES ($1);", username)
    res = Response(status_code=201)
    res.set_cookie(key="access_token", value=generate_jwt(username), httponly=True)
    return res

@app.get("/account/statistics")
async def get_account(username: str = Depends(get_current_user)):
    return await db_query_one(Statistic, "SELECT * FROM Statistics WHERE account_username=$1;", username)

from fastapi import Form, Depends, HTTPException, Response
from hashlib import sha256

from main import app
from .db import db_query_one, db_query, db_execute
from .auth import generate_jwt, get_current_user, JWT_NAME

@app.post("/me")
async def post_me(username: str = Form(...), password: str = Form(...)):
    existing_user = await db_query_one("SELECT username FROM Accounts WHERE username=$1;", username)
    if existing_user is not None:
        raise HTTPException(409, detail="Conflicting username")
    
    password_hash = sha256(password.encode())
    await db_execute("INSERT INTO Accounts (username, password_hash) VALUES ($1, $2);", username, password_hash.hexdigest())

    account_id = await db_query_one("SELECT account_id FROM Accounts WHERE username=$1;", username)
    token = generate_jwt(str(account_id.get("account_id")))

    res = Response(status_code=201)
    res.set_cookie(key=JWT_NAME, value=token, httponly=True)
    return res

# @app.delete("/me", status_code=204, response_description="Deleted account")
# async def delete_me(res: Response, account_id: str = Depends(get_current_user)):

#     res.delete_cookie("access_token")

# @app.post("/token")
# async def post_token(username: str = Form(), password: str = Form()):
#     existing_user = await db_query_one(Account, "SELECT * FROM Accounts WHERE username=$1 AND password=$2;", username, password)
#     if existing_user is None:
#         raise HTTPException(401)
#     res = Response(status_code=201)
#     res.set_cookie(key="access_token", value=generate_jwt(username), httponly=True)
#     return res

# @app.get("/account/statistics")
# async def get_account(username: str = Depends(get_current_user)):
#     return await db_query_one(Statistic, "SELECT * FROM Statistics WHERE account_username=$1;", username)

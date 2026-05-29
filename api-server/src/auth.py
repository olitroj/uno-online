import jwt
import time
import os
from fastapi import Request, HTTPException

JWT_NAME            = os.environ.get("JWT_NAME")
JWT_SECRET          = os.environ.get("JWT_SECRET")
JWT_SESSION_LENGTH  = int(os.environ.get("JWT_SESSION_LENGTH"))

def get_current_user(req: Request) -> str:
    return validate_jwt(req.cookies.get(JWT_NAME))

def generate_jwt(account_id: str):
    payload = {
        "account_id": account_id,
        "expires": int(time.time()) + JWT_SESSION_LENGTH
    }
    return jwt.encode(payload, JWT_SECRET, "HS256")

def validate_jwt(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, "HS256")
        if payload["expires"] > int(time.time()):
            return payload["account_id"]
        else:
            raise HTTPException(401)
    except:
        raise HTTPException(401)
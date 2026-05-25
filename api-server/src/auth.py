from fastapi import Request, HTTPException
import jwt
import time

from main import JWT_SECRET, SESSION_LENGTH, JWT_NAME

def get_current_user(req: Request) -> str:
    return validate_jwt(req.cookies.get(JWT_NAME))

def generate_jwt(account_id: str):
    payload = {
        "account_id": account_id,
        "expires": int(time.time()) + SESSION_LENGTH
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
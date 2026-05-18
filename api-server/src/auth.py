from fastapi import Request, HTTPException
import jwt
import time

from main import JWT_SECRET, SESSION_LENGTH

def get_current_user(req: Request) -> str:
    return validate_jwt(req.cookies.get("access_token"))

def generate_jwt(username: str):
    payload = {
        "username": username,
        "expires": int(time.time()) + SESSION_LENGTH
    }
    return jwt.encode(payload, JWT_SECRET, "HS256")

def validate_jwt(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, "HS256")
        if payload["expires"] > int(time.time()):
            return payload["username"]
        else:
            raise HTTPException(401)
    except:
        raise HTTPException(401)
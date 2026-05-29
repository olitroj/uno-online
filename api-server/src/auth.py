import jwt
import time
import os

JWT_NAME            = os.environ.get("JWT_NAME")
JWT_SECRET          = os.environ.get("JWT_SECRET")
JWT_SESSION_LENGTH  = int(os.environ.get("JWT_SESSION_LENGTH"))

def generate_jwt(account_id: str):
    payload = {
        "account_id": account_id,
        "expires": int(time.time()) + JWT_SESSION_LENGTH
    }
    return jwt.encode(payload, JWT_SECRET, "HS256")

def validate_jwt(token: str) -> str:
    payload = jwt.decode(token, JWT_SECRET, "HS256")
    if payload["expires"] > int(time.time()):
        return payload["account_id"]
    else:
        raise "Token is expired"
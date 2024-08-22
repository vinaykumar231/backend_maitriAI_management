from __future__ import annotations

import time
from typing import Any
import jwt
from decouple import config  #pip install python-decouple
from jwt import PyJWTError


JWT_SECRET = config('SECRET', default='default_secret_key')
JWT_ALGORITHM = config('ALGORITHM', default='HS256')

def signJWT(user_id: str, user_type: str) -> tuple[str, float]:
    expiration_time = time.time() + 1 * 24 * 60 * 60
    payload = {
        "user_id": user_id,
        "user_type": user_type,
        "exp": expiration_time
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, expiration_time

def decodeJWT(token: str) -> dict | None:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if decoded_token.get("exp") and decoded_token["exp"] < time.time():
            return None
        if "user_id" not in decoded_token or "user_type" not in decoded_token:
            return None
        return decoded_token
    except PyJWTError:
        return None




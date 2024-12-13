import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")
jwt_key = os.getenv("JWT_KEY")


def generateAccessToken(email: str):
    return jwt.encode(
        {
            "email": email,
            "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=5 * 60),
        },
        key=jwt_key,
        algorithm="HS256",
    )


def generateRefreshToken(email: str):
    return jwt.encode(
        {"email": email, "exp": datetime.now(tz=timezone.utc) + timedelta(days=10)},
        key=jwt_key,
        algorithm="HS256",
    )


def decodeToken(token):
    return jwt.decode(jwt=token, key=jwt_key, algorithms=["HS256"])

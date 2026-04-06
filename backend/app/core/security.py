from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.config import settings


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": user_id, "exp": expire}, settings.secret_key, algorithm="HS256")


def decode_token(token: str) -> str:
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    return payload["sub"]

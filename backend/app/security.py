import os
from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt

ALGORITHM = "HS256"
COOKIE_NAME = "sutms_access_token"
SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False

def create_access_token(user_id: str, role: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": user_id, "role": role, "exp": expires_at}, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

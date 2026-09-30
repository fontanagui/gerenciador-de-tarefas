from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from jose import jwt
from app.config import settings

password_hasher = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    return password_hasher.hash(password)


def verifica_pswd(password: str, hashed_pswd: str) -> bool:
    return password_hasher.verify(password, hashed_pswd)


def create_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

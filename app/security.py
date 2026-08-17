from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from jose import jwt , JWTError
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY= os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACESS_TOKEN_EXPIRE_MINUTES",30))

password_hasher = PasswordHash.recommended()

def get_password_hash(password:str) -> str:
    return password_hasher.hash(password)


def verifica_pswd (password:str, hashed_pswd:str) -> bool:
    return password_hasher.verify(password, hashed_pswd)

def create_token(data:dict)->str:
    to_encode =data.copy()
    expire=datetime.now(timezone.utc)+timedelta(minutes= ACESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
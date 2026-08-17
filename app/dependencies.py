from collections.abc import Generator
from sqlalchemy.orm import Session
from app.database import SessionLocal
from fastapi import Depends,HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer,HTTPAuthorizationCredentials
from jose import JWTError, jwt
from .security import SECRET_KEY, ALGORITHM
from app.models.user import User


oauth2_scheme = HTTPBearer()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()                                       





def get_current_user(auth:HTTPAuthorizationCredentials=Depends(oauth2_scheme), db:Session = Depends(get_db)):
    token=auth.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais invalidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user
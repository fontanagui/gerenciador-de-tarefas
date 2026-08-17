from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.auth import UserLogin, TokenSchema
from app.services.user_service import UserService
from app.security import create_token



router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenSchema)
def login (userl:UserLogin,db:Session= Depends(get_db)):
    db_user=UserService.autentica_user(db, userl.email, userl.password)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais invalidas", headers={"WWW-Authenticate": "Bearer"})
    access_token = create_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}  
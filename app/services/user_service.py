from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User    
from app.schemas.users import UserCreate, UserUpdate
from fastapi import HTTPException
from app.security import get_password_hash,verifica_pswd

class UserService:
    @staticmethod
    def create_user(db: Session, user: UserCreate):
        existing_user =db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
        if existing_user:
            raise HTTPException(status_code=409, detail="user ja registrado")

        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,   
            password=hashed_password
        )
        db.add(db_user)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail="Conflito nos dados do usuário") from exc
        db.refresh(db_user)
        return db_user


    @staticmethod
    def get_users(db: Session):
        return db.query(User).all()

    @staticmethod
    def get_user(db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User nao encontrado") 
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, updated_user: UserUpdate):
        user_db = db.query(User).filter(User.id == user_id).first()
        if not user_db:
            raise HTTPException(status_code=404, detail="User nao encontrado")
        user_db.username = updated_user.username
        user_db.email = updated_user.email
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail="Conflito nos dados do usuário") from exc
        db.refresh(user_db)
        return user_db



    @staticmethod
    def delete_user(db: Session, user_id: int):
        user_db =db.query(User).filter(User.id == user_id).first()
        if not user_db:
            raise HTTPException(status_code=404, detail="User nao encontrado")
        db.delete(user_db)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail="Conflito nos dados do usuário") from exc
        return {"mensagem": "User deletedo"}


    @staticmethod
    def autentica_user(db:Session, email:str, passwd:str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Credenciais invalidas", headers={"WWW-Authenticate": "Bearer"})
        if not verifica_pswd(passwd, user.password):
            raise HTTPException(status_code=401, detail="Credenciais invalidas", headers={"WWW-Authenticate": "Bearer"})
        return user
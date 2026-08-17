from sqlalchemy.orm import Session
from app.models.user import User    
from app.schemas.users import UserCreate, UserUpdate
from fastapi import HTTPException
from app.security import get_password_hash,verifica_pswd

class UserService:
    @staticmethod
    def create_user(db: Session, user: UserCreate):
        existing_user =db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="user ja registrado")

        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,   
            password=hashed_password
        )
        db.add(db_user)
        db.commit()
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
        db.commit()
        db.refresh(user_db)
        return user_db



    @staticmethod
    def delete_user(db: Session, user_id: int):
        user_db =db.query(User).filter(User.id == user_id).first()
        if not user_db:
            raise HTTPException(status_code=404, detail="User nao encontrado")
        db.delete(user_db)
        db.commit()
        return {"mensagem": "User deletedo"}


    @staticmethod
    def autentica_user(db:Session, email:str, passwd:str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User nao encontrado")
        if not verifica_pswd(passwd, user.password):
            raise HTTPException(status_code=401, detail="Senha incorreta")
        return user
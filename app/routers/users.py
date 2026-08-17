from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models.user import User
from app.schemas.users import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService


router = APIRouter(
    prefix="/users",   
    tags=["users"],
)



@router.get("/" , response_model= list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return UserService.get_users(db)


@router.post("/",  response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return UserService.create_user(db, user)



@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return UserService.get_user(db, user_id)
    
@router.put("/{user_id}", response_model=UserResponse) 
def update_user(user_id: int, updated_user: UserUpdate, db: Session = Depends(get_db)):
    return UserService.update_user(db, user_id, updated_user)

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return UserService.delete_user(db, user_id)
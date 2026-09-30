from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.users import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def require_owner(user_id: int, current_user: User = Depends(get_current_user)) -> User:
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso não permitido")
    return current_user


@router.get("/", response_model=list[UserResponse])
def get_users(current_user: User = Depends(get_current_user)):
    return [current_user]


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return UserService.create_user(db, user)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, current_user: User = Depends(require_owner)):
    return current_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, updated_user: UserUpdate,
                db: Session = Depends(get_db), current_user: User = Depends(require_owner)):
    return UserService.update_user(db, user_id, updated_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db),
                current_user: User = Depends(require_owner)):
    UserService.delete_user(db, user_id)

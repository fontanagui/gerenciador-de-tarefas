from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

@router.post("/", response_model=TaskResponse,status_code=status.HTTP_201_CREATED)
def create_task(
    task:TaskCreate,
    db:Session= Depends(get_db),
    current_user: User=    Depends(get_current_user)
):
    return TaskService.create_task(db=db,task_info=task,user_id=current_user.id)


@router.get ("/", response_model=list[TaskResponse])
def get_tasks(
    db:Session=Depends(get_db),
    current_user:User =Depends(get_current_user)
):
    return TaskService.get_user_task(db=db,user_id=current_user.id)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id:int,db:Session= Depends(get_db),current_user:User=Depends(get_current_user)):
    return TaskService.get_task_byid(db=db,task_id=task_id,user_id=current_user.id)



@router.put("/{task_id}", response_model=TaskResponse)
def put_task(task_id:int,task_update:TaskUpdate,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    return TaskService.update_task(db=db,task_id=task_id,task_data=task_update,user_id=current_user.id)



@router.delete("/{task_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id:int,
    db:Session= Depends(get_db),current_user:User=Depends(get_current_user)
):
    TaskService.delete_task(db=db,task_id=task_id,user_id=current_user.id)
    return None
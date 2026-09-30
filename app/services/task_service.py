from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from fastapi import HTTPException,status













class TaskService:
    @staticmethod
    def create_task(db:Session,task_info:TaskCreate,user_id:int) -> Task:
        db_task= Task(**task_info.model_dump(),
            user_id=user_id)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task


    @staticmethod
    def get_user_task(db: Session, user_id: int, offset: int = 0, limit: int = 50):
        return db.query(Task).filter(Task.user_id==user_id).order_by(Task.id).offset(offset).limit(limit).all()

    @staticmethod
    def get_task_byid(db:Session,task_id:int,user_id:int)-> Task:
        task= db.query(Task).filter(Task.id==task_id, Task.user_id==user_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarefa nao encontrada"
            )
        return task


    @staticmethod
    def update_task(db:Session,task_id:int,task_data:TaskUpdate,user_id:int)->Task:
        task=TaskService.get_task_byid(db,task_id,user_id)
        update_data=task_data.model_dump(exclude_unset=True)
        for key,value in update_data.items():
            setattr(task,key,value)
        db.commit()
        db.refresh(task)
        return task



    @staticmethod
    def delete_task(db:Session,task_id:int,user_id:int):
        task=TaskService.get_task_byid(db,task_id,user_id)
        db.delete(task)
        db.commit()



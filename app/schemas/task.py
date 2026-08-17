from pydantic import BaseModel, EmailStr
from typing import Optional

class TaskBase (BaseModel):
    title:str
    descricao:Optional[str] = None
    concluida: Optional[bool]=False

class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    titulo: Optional[str] = None    
    descricao: Optional[str] = None 
    completa: Optional[bool] = None


class TaskResponse(TaskBase):
    id: int
    user_id:int

    class Config:
        from_attributes= True
        
from fastapi import FastAPI
from app.database import engine,Base
from app.models import User
from .routers.users import router as user_router
from .routers.auth import router as auth_router
from .routers.tasks import router as tasks_router
Base.metadata.create_all(bind=engine) 

app = FastAPI(
    title="Gerenciador de Tarefas", 
)

app.include_router(user_router)
app.include_router(auth_router)  
app.include_router(tasks_router)



@app.get("/")
def root():  
    return {"message": "Bem-vindo ao Gerenciador de Tarefas!"}

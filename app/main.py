from pathlib import Path
from fastapi.staticfiles import StaticFiles
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


# The frontend is optional: build it with npm run build in frontend/.
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.is_dir():
    app.mount("/ui", StaticFiles(directory=frontend_dist, html=True), name="frontend")

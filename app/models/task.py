from sqlalchemy import Column, Integer, String,Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column (Integer,primary_key = True, index= True)
    title = Column(String(150), nullable= False)
    descricao= Column(String(350), nullable = True)
    concluida= Column(Boolean, default= False)
    user_id = Column(Integer, ForeignKey("users.id"),nullable= False)



    owner = relationship("User", back_populates="tasks")
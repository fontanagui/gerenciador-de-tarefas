from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.database import Base



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    username: Mapped[str] = mapped_column(String(70), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)




    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")
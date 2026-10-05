from sqlalchemy import Boolean, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base

class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        Index(
            "ix_tasks_completed_priority", 
            "completed",
            "priority",
        ),
    )
    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True
    )
    title: Mapped[str] = mapped_column(
        String(120), 
        nullable=False,
        index=True,)
    completed: Mapped[bool] = mapped_column(
        Boolean, 
        default=False,
        nullable=False,)
    priority: Mapped[int] = mapped_column(
        Integer, 
        default=3,
        nullable=False,
    )
from sqlalchemy import Column, Integer, String, Text, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import enum

class TaskStatus(str, enum.Enum):
    todo = "To-Do"
    in_progress = "In Progress"
    done = "Done"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.todo, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)
    
    # Self-referential foreign key for "Blocked By"
    blocked_by_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)

    # Relationships
    blocked_by = relationship("Task", remote_side=[id], foreign_keys=[blocked_by_id])
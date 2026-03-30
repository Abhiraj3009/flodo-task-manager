from pydantic import BaseModel
from datetime import date
from typing import Optional
from models import TaskStatus

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: TaskStatus = TaskStatus.todo
    blocked_by_id: Optional[int] = None
    order_index: Optional[int] = 0

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    title: Optional[str] = None
    status: Optional[TaskStatus] = None

class TaskResponse(TaskBase):
    id: int
    blocked_by: Optional["TaskResponse"] = None

    class Config:
        from_attributes = True

class ReorderRequest(BaseModel):
    task_ids: list[int]
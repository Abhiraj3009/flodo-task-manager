from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from database import get_db
from models import Task
from schemas import TaskCreate, TaskUpdate, TaskResponse, ReorderRequest
from typing import Optional
import asyncio

router = APIRouter(prefix="/tasks", tags=["tasks"])


# GET all tasks (with optional search & filter)
@router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Task).order_by(Task.order_index)

    if search:
        query = query.where(Task.title.ilike(f"%{search}%"))
    if status:
        query = query.where(Task.status == status)

    result = await db.execute(query)
    return result.scalars().all()


# GET single task
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# POST create task (with 2 second simulated delay)
@router.post("/", response_model=TaskResponse)
async def create_task(task_data: TaskCreate, db: AsyncSession = Depends(get_db)):
    await asyncio.sleep(2)  # Simulated delay

    new_task = Task(**task_data.model_dump())
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task


# PUT update task (with 2 second simulated delay)
@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    await asyncio.sleep(2)  # Simulated delay

    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for key, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)
    return task


# DELETE task
@router.delete("/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.delete(task)
    await db.commit()
    return {"message": "Task deleted successfully"}


# PATCH reorder tasks (drag-and-drop stretch goal)
@router.patch("/reorder/batch")
async def reorder_tasks(
    reorder_data: ReorderRequest,
    db: AsyncSession = Depends(get_db)
):
    for index, task_id in enumerate(reorder_data.task_ids):
        await db.execute(
            update(Task).where(Task.id == task_id).values(order_index=index)
        )
    await db.commit()
    return {"message": "Tasks reordered successfully"}
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from repositories.task import TaskRepository
from repositories.user import UserRepository
from db.models.user import User

from schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter()


# CREATE TASK
@router.post("/", response_model=TaskRead)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    task = TaskRepository(db).create_task(task=payload)
    return task


# LIST TASKS
@router.get("/", response_model=dict)
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    return TaskRepository(db).get_tasks(skip=skip, limit=limit)


# GET ONE TASK
@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    return TaskRepository(db).get_task_by_id(task_id)


# UPDATE TASK
@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    return TaskRepository(db).update_task(task_id, payload)


# DELETE TASK
@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    return TaskRepository(db).delete_task(task_id)
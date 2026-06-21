from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from repositories.task import TaskRepository
from repositories.user import UserRepository
from db.models.user import User

from schemas.task import (
    TaskCreate,
    TaskRead,
    TaskUpdate,
)

router = APIRouter()


# CREATE TASK
@router.post("", response_model=TaskRead)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    task_repo = TaskRepository(db=db)

    return task_repo.create_task(
        task=payload
    )


# LIST TASKS
@router.get("")
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    task_repo = TaskRepository(db=db)

    return task_repo.get_tasks(
        skip=skip,
        limit=limit
    )


# GET SINGLE TASK
@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    task_repo = TaskRepository(db=db)

    return task_repo.get_task_by_id(
        task_id=task_id
    )


# UPDATE TASK
@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    task_repo = TaskRepository(db=db)

    return task_repo.update_task(
        task_id=task_id,
        payload=payload
    )


# DELETE TASK
@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    task_repo = TaskRepository(db=db)

    return task_repo.delete_task(
        task_id=task_id
    )
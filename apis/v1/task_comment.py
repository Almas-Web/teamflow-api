from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from repositories.task_comment import TaskCommentRepository
from repositories.user import UserRepository
from db.models.user import User

from schemas.task_comment import (
    TaskCommentCreate,
    TaskCommentRead,
    TaskCommentUpdate,
)

router = APIRouter()


# CREATE COMMENT
@router.post("", response_model=TaskCommentRead)
def create_comment(
    payload: TaskCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    repo = TaskCommentRepository(db=db)

    return repo.create_comment(
        payload=payload,
        user_id=current_user.id
    )


# GET COMMENTS BY TASK
@router.get("/task/{task_id}")
def get_comments_by_task(
    task_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    repo = TaskCommentRepository(db=db)

    return repo.get_comments_by_task(
        task_id=task_id,
        skip=skip,
        limit=limit
    )


# GET SINGLE COMMENT
@router.get("/{comment_id}", response_model=TaskCommentRead)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    repo = TaskCommentRepository(db=db)

    return repo.get_comment_by_id(
        comment_id=comment_id
    )


# UPDATE COMMENT
@router.put("/{comment_id}", response_model=TaskCommentRead)
def update_comment(
    comment_id: int,
    payload: TaskCommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    repo = TaskCommentRepository(db=db)

    return repo.update_comment(
        comment_id=comment_id,
        payload=payload
    )


# DELETE COMMENT
@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    repo = TaskCommentRepository(db=db)

    return repo.delete_comment(
        comment_id=comment_id
    )
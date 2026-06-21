from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from repositories.notification import NotificationRepository
from repositories.user import UserRepository
from db.models.user import User

from schemas.notification import (
    NotificationCreate,
    NotificationRead,
    NotificationUpdate,
)

router = APIRouter()


# CREATE NOTIFICATION
@router.post("", response_model=NotificationRead)
def create_notification(
    payload: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    repo = NotificationRepository(db=db)

    return repo.create_notification(
        payload=payload
    )


# GET NOTIFICATIONS (BY USER)
@router.get("")
def get_notifications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    repo = NotificationRepository(db=db)

    return repo.get_notifications(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )


# MARK AS READ
@router.put("/{notification_id}/read", response_model=NotificationRead)
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    repo = NotificationRepository(db=db)

    return repo.mark_as_read(
        notification_id=notification_id
    )


# DELETE NOTIFICATION
@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    repo = NotificationRepository(db=db)

    return repo.delete_notification(
        notification_id=notification_id
    )
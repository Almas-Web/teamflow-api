from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from db.models.notification import Notification
from schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
)


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    # Helper
    def get_notification_or_404(self, notification_id: int) -> Notification:
        notification = (
            self.db.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )

        if not notification:
            raise HTTPException(
                status_code=404,
                detail="Notification not found"
            )

        return notification

    # CREATE NOTIFICATION
    def create_notification(
        self,
        payload: NotificationCreate
    ) -> Notification:

        db_notification = Notification(
            user_id=payload.user_id,
            message=payload.message,
            is_read=False
        )

        try:
            self.db.add(db_notification)
            self.db.commit()
            self.db.refresh(db_notification)

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Something went wrong!"
            )

        return db_notification

    # LIST NOTIFICATIONS (BY USER)
    def get_notifications(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ):
        total_count = (
            self.db.query(func.count(Notification.id))
            .filter(Notification.user_id == user_id)
            .scalar()
        )

        notifications = (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

        return {
            "total_count": total_count,
            "skip": skip,
            "limit": limit,
            "data": notifications
        }

    # MARK AS READ
    def mark_as_read(
        self,
        notification_id: int
    ) -> Notification:

        notification = self.get_notification_or_404(notification_id)

        notification.is_read = True

        self.db.commit()
        self.db.refresh(notification)

        return notification

    # DELETE NOTIFICATION
    def delete_notification(
        self,
        notification_id: int
    ):

        notification = self.get_notification_or_404(notification_id)

        self.db.delete(notification)
        self.db.commit()

        return {
            "message": "Notification deleted successfully"
        }
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from db.models.task import Task
from db.models.task_comment import TaskComment
from schemas.task_comment import (
    TaskCommentCreate,
    TaskCommentUpdate,
)


class TaskCommentRepository:
    def __init__(self, db: Session):
        self.db = db

    # Helper (REUSABLE)
    def get_comment_or_404(self, comment_id: int) -> TaskComment:
        comment = (
            self.db.query(TaskComment)
            .filter(TaskComment.id == comment_id)
            .first()
        )

        if not comment:
            raise HTTPException(
                status_code=404,
                detail="Comment not found"
            )

        return comment

    # CREATE COMMENT
    def create_comment(
        self,
        payload: TaskCommentCreate,
        user_id: int
    ) -> TaskComment:

        # check task exists
        task = (
            self.db.query(Task)
            .filter(Task.id == payload.task_id)
            .first()
        )

        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        db_comment = TaskComment(
            task_id=payload.task_id,
            user_id=user_id,
            comment=payload.comment
        )

        try:
            self.db.add(db_comment)
            self.db.commit()
            self.db.refresh(db_comment)

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Something went wrong!"
            )

        return db_comment

    # GET COMMENTS BY TASK
    def get_comments_by_task(
        self,
        task_id: int,
        skip: int = 0,
        limit: int = 100
    ):
        total_count = (
            self.db.query(func.count(TaskComment.id))
            .filter(TaskComment.task_id == task_id)
            .scalar()
        )

        comments = (
            self.db.query(TaskComment)
            .filter(TaskComment.task_id == task_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

        return {
            "total_count": total_count,
            "skip": skip,
            "limit": limit,
            "data": comments
        }

    # GET ONE COMMENT
    def get_comment_by_id(
        self,
        comment_id: int
    ) -> TaskComment:

        return self.get_comment_or_404(comment_id)

    # UPDATE COMMENT
    def update_comment(
        self,
        comment_id: int,
        payload: TaskCommentUpdate
    ) -> TaskComment:

        comment = self.get_comment_or_404(comment_id)

        update_data = payload.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(comment, key, value)

        self.db.commit()
        self.db.refresh(comment)

        return comment

    # DELETE COMMENT
    def delete_comment(
        self,
        comment_id: int
    ):

        comment = self.get_comment_or_404(comment_id)

        self.db.delete(comment)
        self.db.commit()

        return {
            "message": "Comment deleted successfully"
        }
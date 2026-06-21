from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from db.models.task import Task
from schemas.task import TaskCreate, TaskUpdate


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    # Helper (REUSABLE)
    def get_task_or_404(self, task_id: int) -> Task:
        task = (
            self.db.query(Task)
            .filter(Task.id == task_id)
            .first()
        )

        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        return task

    # CREATE TASK
    def create_task(
        self,
        task: TaskCreate
    ) -> Task:

        db_task = Task(
            project_id=task.project_id,
            assigned_to=task.assigned_to,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date
        )

        try:
            self.db.add(db_task)
            self.db.commit()
            self.db.refresh(db_task)

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Something went wrong!"
            )

        return db_task

    # LIST TASKS
    def get_tasks(
        self,
        skip: int = 0,
        limit: int = 100
    ):
        total_count = (
            self.db.query(func.count(Task.id)).scalar()
        )

        tasks = (
            self.db.query(Task)
            .offset(skip)
            .limit(limit)
            .all()
        )

        return {
            "total_count": total_count,
            "skip": skip,
            "limit": limit,
            "data": tasks
        }

    # GET ONE TASK
    def get_task_by_id(
        self,
        task_id: int
    ) -> Task:

        return self.get_task_or_404(task_id)

    # UPDATE TASK
    def update_task(
        self,
        task_id: int,
        payload: TaskUpdate
    ) -> Task:

        task = self.get_task_or_404(task_id)

        update_data = payload.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(task, key, value)

        self.db.commit()
        self.db.refresh(task)

        return task

    # DELETE TASK
    def delete_task(
        self,
        task_id: int
    ):

        task = self.get_task_or_404(task_id)

        self.db.delete(task)
        self.db.commit()

        return {
            "message": "Task deleted successfully"
        }
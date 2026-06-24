from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from db.models.task import Task
from schemas.task import TaskCreate, TaskUpdate, TaskRead


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_task_or_404(self, task_id: int) -> Task:
        task = self.db.query(Task).filter(Task.id == task_id).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        return task

    # CREATE
    def create_task(self, task: TaskCreate) -> TaskRead:
        db_task = Task(**task.model_dump())

        try:
            self.db.add(db_task)
            self.db.commit()
            self.db.refresh(db_task)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Something went wrong!")

        return TaskRead.model_validate(db_task)

    # LIST (🔥 FIXED)
    def get_tasks(self, skip: int = 0, limit: int = 100):

        total_count = self.db.query(func.count(Task.id)).scalar()

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
            "data": [TaskRead.model_validate(t) for t in tasks]
        }

    def get_task_by_id(self, task_id: int) -> TaskRead:
        task = self.get_task_or_404(task_id)
        return TaskRead.model_validate(task)

    def update_task(self, task_id: int, payload: TaskUpdate) -> TaskRead:
        task = self.get_task_or_404(task_id)

        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(task, key, value)

        self.db.commit()
        self.db.refresh(task)

        return TaskRead.model_validate(task)

    def delete_task(self, task_id: int):
        task = self.get_task_or_404(task_id)

        self.db.delete(task)
        self.db.commit()

        return {"message": "Task deleted successfully"}
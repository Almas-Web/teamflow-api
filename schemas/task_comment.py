from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TaskCommentCreate(BaseModel):
    task_id: int
    comment: str


class TaskCommentUpdate(BaseModel):
    comment: str | None = None


class TaskCommentRead(BaseModel):
    id: int
    task_id: int
    user_id: int
    comment: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    project_id: int
    assigned_to: int | None = None

    title: str
    description: str | None = None

    status: str = "todo"
    priority: str = "medium"
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None

    status: str | None = None
    priority: str | None = None

    assigned_to: int | None = None
    due_date: datetime | None = None


class TaskRead(BaseModel):
    id: int
    project_id: int
    assigned_to: int | None = None

    title: str
    description: str | None = None

    status: str
    priority: str

    due_date: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
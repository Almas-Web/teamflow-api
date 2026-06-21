from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    workspace_id: int
    name: str
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectRead(BaseModel):
    id: int
    workspace_id: int
    name: str
    description: str | None = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
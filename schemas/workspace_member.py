from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class WorkspaceMemberCreate(BaseModel):
    user_id: int
    role: str | None = "member"


class WorkspaceMemberUpdate(BaseModel):
    role: str | None = None


class WorkspaceMemberRead(BaseModel):
    id: int
    workspace_id: int
    user_id: int
    role: str
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)
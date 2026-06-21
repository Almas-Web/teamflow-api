from datetime import datetime
from pydantic import BaseModel, ConfigDict


# CREATE INVITATION
class InvitationCreate(BaseModel):
    workspace_id: int
    email: str


# ACCEPT INVITATION
class InvitationAccept(BaseModel):
    token: str


# READ INVITATION
class InvitationRead(BaseModel):
    id: int
    workspace_id: int
    email: str
    token: str
    status: str
    expires_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
from datetime import datetime
from pydantic import BaseModel, ConfigDict


# CREATE NOTIFICATION
class NotificationCreate(BaseModel):
    user_id: int
    message: str


# UPDATE / MARK READ
class NotificationUpdate(BaseModel):
    is_read: bool | None = None


# READ NOTIFICATION
class NotificationRead(BaseModel):
    id: int
    user_id: int
    message: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recipient_id: UUID
    emergency_id: UUID | None
    notification_type: str
    title: str
    message: str
    channel: str
    is_read: bool
    created_at: datetime


class NotificationReadUpdate(BaseModel):
    is_read: bool = True

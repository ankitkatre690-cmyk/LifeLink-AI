from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DispatchCreate(BaseModel):
    emergency_id: UUID


class DispatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    emergency_id: UUID
    assignment_id: UUID
    hospital_id: UUID | None
    distance_km: float
    eta_minutes: int
    dispatch_status: str
    created_at: datetime


class DispatchLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    dispatch_id: UUID
    status: str
    message: str | None
    created_at: datetime

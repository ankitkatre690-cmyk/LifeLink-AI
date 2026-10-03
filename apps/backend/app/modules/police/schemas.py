from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PoliceCaseCreate(BaseModel):
    notes: str | None = Field(default=None, max_length=2000)


class PoliceCaseUpdate(BaseModel):
    case_status: str
    notes: str | None = Field(default=None, max_length=2000)


class PoliceCaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    emergency_id: UUID
    police_user_id: UUID
    case_status: str
    notes: str | None
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class PoliceActiveEmergencyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    citizen_id: UUID
    emergency_type: str
    severity: str
    status: str
    latitude: float
    longitude: float
    description: str | None
    created_at: datetime

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


ALLOWED_EMERGENCY_TYPES = {
    "Medical",
    "Accident",
    "Fire",
    "Crime",
    "Other",
}


class EmergencyCreate(BaseModel):
    emergency_type: str = Field(min_length=1, max_length=50)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("emergency_type")
    @classmethod
    def validate_emergency_type(cls, value: str) -> str:
        normalized = value.strip()
        if normalized not in ALLOWED_EMERGENCY_TYPES:
            raise ValueError(
                "Emergency type must be one of: Medical, Accident, Fire, Crime, Other."
            )
        return normalized

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class EmergencyUpdateRequest(BaseModel):
    status: str = Field(min_length=1, max_length=32)
    remarks: str | None = Field(default=None, max_length=2000)


class EmergencyResponse(BaseModel):
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


class EmergencyTimelineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    emergency_id: UUID
    updated_by: UUID
    status: str
    remarks: str | None
    created_at: datetime

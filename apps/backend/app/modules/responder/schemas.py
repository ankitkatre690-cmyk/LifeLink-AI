from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ResponderCreate(BaseModel):
    responder_type: str = Field(min_length=2, max_length=50)
    vehicle_number: str | None = Field(default=None, max_length=50)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class ResponderStatusUpdate(BaseModel):
    status: str = Field(min_length=2, max_length=20)


class ResponderLocationUpdate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class ResponderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    responder_type: str
    status: str
    vehicle_number: str | None
    latitude: float | None
    longitude: float | None


class AssignmentCreate(BaseModel):
    emergency_id: UUID
    distance_km: float | None = Field(default=None, ge=0)
    eta_minutes: int | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=500)


class AssignmentStatusUpdate(BaseModel):
    status: str = Field(min_length=2, max_length=30)
    notes: str | None = Field(default=None, max_length=500)


class AssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    emergency_id: UUID
    responder_id: UUID
    status: str
    distance_km: float | None
    eta_minutes: int | None
    notes: str | None

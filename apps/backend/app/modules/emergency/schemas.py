from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# -------------------------
# Create Emergency
# -------------------------

class EmergencyCreate(BaseModel):
    emergency_type: str
    latitude: float
    longitude: float
    description: str | None = None


# -------------------------
# Update Emergency
# -------------------------

class EmergencyUpdateRequest(BaseModel):
    status: str
    remarks: str | None = None


# -------------------------
# Emergency Response
# -------------------------

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


# -------------------------
# Timeline Response
# -------------------------

class EmergencyTimelineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    emergency_id: UUID
    updated_by: UUID
    status: str
    remarks: str | None
    created_at: datetime
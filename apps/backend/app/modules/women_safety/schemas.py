from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WomenSafetyProfileCreate(BaseModel):
    enabled: bool = True
    safe_word: str | None = Field(default=None, min_length=2, max_length=50)
    auto_share_location: bool = True


class WomenSafetyProfileUpdate(BaseModel):
    enabled: bool | None = None
    safe_word: str | None = Field(default=None, min_length=2, max_length=50)
    auto_share_location: bool | None = None


class WomenSafetyProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    enabled: bool
    safe_word: str | None
    auto_share_location: bool
    created_at: datetime
    updated_at: datetime


class WomenSafetySOSRequest(BaseModel):
    latitude: float
    longitude: float
    description: str | None = Field(default=None, max_length=1000)


class WomenSafetySOSResponse(BaseModel):
    emergency_id: UUID
    emergency_type: str
    severity: str
    status: str
    location_shared: bool
    message: str

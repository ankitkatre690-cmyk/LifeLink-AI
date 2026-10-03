from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HospitalCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    address: str = Field(min_length=2, max_length=300)
    phone: str = Field(min_length=5, max_length=20)


class HospitalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    name: str
    address: str
    phone: str
    is_active: bool


class ResourceCreate(BaseModel):
    resource_type: str = Field(min_length=2, max_length=50)
    total_count: int = Field(ge=0)
    available_count: int = Field(ge=0)


class ResourceUpdate(BaseModel):
    total_count: int = Field(ge=0)
    available_count: int = Field(ge=0)
    is_available: bool = True


class ResourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    hospital_id: UUID
    resource_type: str
    total_count: int
    available_count: int
    is_available: bool

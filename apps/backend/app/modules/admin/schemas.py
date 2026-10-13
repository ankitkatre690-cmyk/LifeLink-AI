from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AdminDashboardResponse(BaseModel):
    users: int
    active_users: int
    emergencies: int
    active_emergencies: int
    responders: int
    available_responders: int
    hospitals: int
    active_hospitals: int
    police_cases: int
    open_police_cases: int


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    phone: str
    role_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AdminUserStatusUpdate(BaseModel):
    is_active: bool

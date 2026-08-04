from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CitizenProfileCreate(BaseModel):
    first_name: str
    last_name: str
    gender: str
    date_of_birth: date
    blood_group: str

    address: str
    city: str
    state: str
    country: str
    pincode: str

    emergency_contact_name: str
    emergency_contact_phone: str

    allergies: str | None = None
    medical_conditions: str | None = None
    medications: str | None = None

    organ_donor: bool = False

    height: float | None = None
    weight: float | None = None


class CitizenProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID

    first_name: str
    last_name: str
    gender: str
    date_of_birth: date
    blood_group: str

    address: str
    city: str
    state: str
    country: str
    pincode: str

    emergency_contact_name: str
    emergency_contact_phone: str

    allergies: str | None
    medical_conditions: str | None
    medications: str | None

    organ_donor: bool

    height: float | None
    weight: float | None
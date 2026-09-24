from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, model_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    phone: str
    password: str
    role: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    phone: str
    is_active: bool
    is_verified: bool
    role: str | None = None

    @model_validator(mode="before")
    @classmethod
    def extract_role_name(cls, value):
        if isinstance(value, dict):
            return value
        role = getattr(value, "role", None)
        if role is not None:
            return {
                "id": value.id,
                "email": value.email,
                "phone": value.phone,
                "is_active": value.is_active,
                "is_verified": value.is_verified,
                "role": getattr(role, "name", None),
            }
        return value

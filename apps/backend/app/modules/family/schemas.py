from uuid import UUID

from pydantic import BaseModel, ConfigDict


# -----------------------------
# Create Family
# -----------------------------

class FamilyCreate(BaseModel):
    name: str


# -----------------------------
# Family Response
# -----------------------------

class FamilyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    created_by: UUID


# -----------------------------
# Add Member
# -----------------------------

class FamilyMemberCreate(BaseModel):
    user_id: UUID
    relationship: str
    is_guardian: bool = False


# -----------------------------
# Family Member Response
# -----------------------------

class FamilyMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    family_group_id: UUID
    user_id: UUID
    relationship: str
    is_guardian: bool
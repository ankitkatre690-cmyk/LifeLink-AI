from pydantic import BaseModel, Field

class DeviceTokenCreate(BaseModel):
    token: str = Field(min_length=1, max_length=512)
    platform: str = Field(min_length=1, max_length=20)

class DeviceTokenResponse(BaseModel):
    id: str
    token: str
    platform: str
    is_active: bool

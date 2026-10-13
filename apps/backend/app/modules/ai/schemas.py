from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field

class EmergencyRiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class AISignalInput(BaseModel):
    activity_score: float = Field(default=0.0, ge=0.0, le=1.0)
    voice_score: float = Field(default=0.0, ge=0.0, le=1.0)
    vision_score: float = Field(default=0.0, ge=0.0, le=1.0)
    sensor_score: float = Field(default=0.0, ge=0.0, le=1.0)

class AIRiskAssessmentResponse(BaseModel):
    risk_score: float
    risk_level: EmergencyRiskLevel
    recommended_action: str
    contributing_signals: list[str]

class AIEmergencyDetectionRequest(AISignalInput):
    latitude: float
    longitude: float
    emergency_type: str = Field(default="AIDetectedEmergency", max_length=50)
    description: str | None = Field(default=None, max_length=1000)

class AIEmergencyDetectionResponse(AIRiskAssessmentResponse):
    emergency_id: UUID | None
    emergency_created: bool

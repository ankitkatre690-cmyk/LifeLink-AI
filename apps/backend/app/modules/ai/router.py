from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.models.user import User
from app.database.session import get_db
from app.modules.ai.schemas import AIEmergencyDetectionRequest, AIEmergencyDetectionResponse, AISignalInput, AIRiskAssessmentResponse
from app.modules.ai.service import AIService
from app.modules.auth.dependencies import get_current_user

router = APIRouter(prefix="/ai", tags=["AI Emergency Detection"])

@router.post("/risk-assessment", response_model=AIRiskAssessmentResponse)
def risk_assessment(request: AISignalInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AIService(db).assess(request)

@router.post("/detect-emergency", response_model=AIEmergencyDetectionResponse)
def detect_emergency(request: AIEmergencyDetectionRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AIService(db).detect_and_create(current_user.id, request)

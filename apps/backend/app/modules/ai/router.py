from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.models.user import User
from app.database.session import get_db
from app.modules.ai.schemas import (
    AIEmergencyDetectionRequest,
    AIEmergencyDetectionResponse,
    AIRiskAssessmentResponse,
    AISignalInput,
    EmergencyRiskLevel,
)
from app.modules.ai.service import AIService
from app.modules.auth.dependencies import get_current_user
from app.modules.dispatch.exceptions import (
    DispatchAlreadyExists,
    NoAvailableHospitalResource,
    NoAvailableResponder,
)
from app.modules.dispatch.repository import DispatchRepository
from app.modules.dispatch.service import DispatchService
from app.realtime.events import build_event
from app.realtime.manager import connection_manager


router = APIRouter(prefix="/ai", tags=["AI Emergency Detection"])


@router.post("/risk-assessment", response_model=AIRiskAssessmentResponse)
def risk_assessment(
    request: AISignalInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AIService(db).assess(request)


@router.post(
    "/detect-emergency",
    response_model=AIEmergencyDetectionResponse,
)
async def detect_emergency(
    request: AIEmergencyDetectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = AIService(db).detect_and_create(current_user.id, request)

    if not result.emergency_created or result.emergency_id is None:
        return result

    dispatch_created = False

    # Critical AI detections are allowed to enter the existing dispatch
    # engine directly. High-risk detections create the emergency and notify
    # the response pipeline; dispatch remains an explicit operational action.
    if result.risk_level is EmergencyRiskLevel.CRITICAL:
        try:
            DispatchService(DispatchRepository(db)).dispatch_emergency(
                result.emergency_id
            )
            dispatch_created = True
        except (NoAvailableResponder, NoAvailableHospitalResource, DispatchAlreadyExists):
            # The emergency remains persisted as Pending when immediate
            # dispatch cannot currently be completed. Operators can retry
            # through the existing dispatch workflow.
            dispatch_created = False

    await connection_manager.send_to_user(
        current_user.id,
        build_event(
            "ai.emergency_detected",
            {
                "emergency_id": str(result.emergency_id),
                "risk_score": result.risk_score,
                "risk_level": result.risk_level.value,
                "emergency_created": True,
                "dispatch_created": dispatch_created,
            },
        ),
    )

    return result

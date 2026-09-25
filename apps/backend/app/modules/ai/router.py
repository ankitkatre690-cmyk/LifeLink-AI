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
from app.modules.family.repository import FamilyRepository
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
    dispatch = None
    if result.risk_level is EmergencyRiskLevel.CRITICAL:
        try:
            dispatch = DispatchService(DispatchRepository(db)).dispatch_emergency(
                result.emergency_id
            )
            dispatch_created = True
        except (NoAvailableResponder, NoAvailableHospitalResource, DispatchAlreadyExists):
            # The emergency remains persisted as Pending when immediate
            # dispatch cannot currently be completed. Operators can retry
            # through the existing dispatch workflow.
            dispatch_created = False

    if dispatch_created and dispatch is not None:
        dispatch_event = build_event(
            "dispatch.assigned",
            {
                "dispatch_id": str(dispatch.id),
                "emergency_id": str(dispatch.emergency_id),
                "responder_id": str(dispatch.assignment.responder_id),
                "hospital_id": str(dispatch.hospital_id) if dispatch.hospital_id else None,
                "distance_km": dispatch.distance_km,
                "eta_minutes": dispatch.eta_minutes,
                "status": dispatch.dispatch_status,
            },
        )
        await connection_manager.send_to_user(dispatch.emergency.citizen_id, dispatch_event)
        for user_id in FamilyRepository(db).get_member_user_ids_for_creator(
            dispatch.emergency.citizen_id
        ):
            await connection_manager.send_to_user(user_id, dispatch_event)

        await connection_manager.send_to_user(
            dispatch.assignment.responder.user_id,
            build_event(
                "dispatch.assignment",
                {
                    "dispatch_id": str(dispatch.id),
                    "emergency_id": str(dispatch.emergency_id),
                    "assignment_id": str(dispatch.assignment_id),
                    "distance_km": dispatch.distance_km,
                    "eta_minutes": dispatch.eta_minutes,
                    "status": dispatch.dispatch_status,
                },
            ),
        )

        if dispatch.hospital is not None:
            await connection_manager.send_to_user(
                dispatch.hospital.user_id,
                build_event(
                    "dispatch.hospital_incoming",
                    {
                        "dispatch_id": str(dispatch.id),
                        "emergency_id": str(dispatch.emergency_id),
                        "hospital_id": str(dispatch.hospital_id),
                        "status": dispatch.dispatch_status,
                    },
                ),
            )

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

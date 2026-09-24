from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from app.realtime.events import build_event
from app.realtime.manager import connection_manager
from sqlalchemy.orm import Session

from app.database.models.user import User
from app.modules.family.repository import FamilyRepository
from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.emergency.exceptions import EmergencyNotFound
from app.modules.emergency.repository import EmergencyRepository
from app.modules.emergency.schemas import (
    EmergencyCreate,
    EmergencyResponse,
    EmergencyTimelineResponse,
    EmergencyUpdateRequest,
)
from app.modules.emergency.service import EmergencyService

router = APIRouter(
    prefix="/emergency",
    tags=["Emergency"],
)


# ---------------------------------------
# Create Emergency
# ---------------------------------------

@router.post(
    "",
    response_model=EmergencyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_emergency(
    request: EmergencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EmergencyService(EmergencyRepository(db))
    if current_user.role is None or current_user.role.name != "Citizen":
        raise HTTPException(403, "Only Citizen users can create emergencies.")

    emergency = service.create_emergency(current_user.id, request)

    event = build_event("emergency.created", {
        "emergency_id": str(emergency.id),
        "citizen_id": str(emergency.citizen_id),
        "status": emergency.status,
        "severity": emergency.severity,
        "emergency_type": emergency.emergency_type,
    })
    await connection_manager.send_to_user(emergency.citizen_id, event)

    for user_id in FamilyRepository(db).get_member_user_ids_for_creator(
        emergency.citizen_id
    ):
        await connection_manager.send_to_user(user_id, event)

    return emergency


# ---------------------------------------
# Get Emergency
# ---------------------------------------

@router.get(
    "/{emergency_id}",
    response_model=EmergencyResponse,
)
def get_emergency(
    emergency_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EmergencyService(EmergencyRepository(db))

    try:
        emergency = service.get_emergency(emergency_id)
        if (
            emergency.citizen_id != current_user.id
            and current_user.role is not None
            and current_user.role.name not in {"Police", "Admin", "Responder"}
        ):
            raise HTTPException(403, "You are not authorized to view this emergency.")
        if (
            emergency.citizen_id != current_user.id
            and (current_user.role is None or current_user.role.name not in {"Police", "Admin", "Responder"})
        ):
            raise HTTPException(403, "You are not authorized to view this emergency.")
        return emergency

    except EmergencyNotFound:
        raise HTTPException(
            status_code=404,
            detail="Emergency not found.",
        )


# ---------------------------------------
# Update Emergency Status
# ---------------------------------------

@router.patch(
    "/{emergency_id}",
    response_model=EmergencyResponse,
)
async def update_status(
    emergency_id: UUID,
    request: EmergencyUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EmergencyService(EmergencyRepository(db))

    try:
        emergency = service.get_emergency(emergency_id)

        if current_user.role is None:
            raise HTTPException(403, "You are not authorized to update this emergency.")

        if current_user.role.name == "Citizen":
            if emergency.citizen_id != current_user.id or request.status != "Cancelled":
                raise HTTPException(
                    403,
                    "Citizens can only cancel their own emergencies.",
                )
        elif current_user.role.name not in {"Police", "Admin"}:
            raise HTTPException(
                403,
                "Use the responder assignment workflow to update responder-managed status.",
            )

        emergency = service.update_status(
            emergency_id,
            current_user.id,
            request,
        )
        event = build_event("emergency.status_changed", {
            "emergency_id": str(emergency.id),
            "citizen_id": str(emergency.citizen_id),
            "status": emergency.status,
            "severity": emergency.severity,
        })
        await connection_manager.send_to_user(emergency.citizen_id, event)
        for user_id in FamilyRepository(db).get_member_user_ids_for_creator(emergency.citizen_id):
            await connection_manager.send_to_user(user_id, event)
        return emergency

    except EmergencyNotFound:
        raise HTTPException(
            status_code=404,
            detail="Emergency not found.",
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


# ---------------------------------------
# Emergency Timeline
# ---------------------------------------

@router.get(
    "/{emergency_id}/timeline",
    response_model=list[EmergencyTimelineResponse],
)
def get_timeline(
    emergency_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EmergencyService(EmergencyRepository(db))
    try:
        emergency = service.get_emergency(emergency_id)
        if (
            emergency.citizen_id != current_user.id
            and (
                current_user.role is None
                or current_user.role.name not in {"Police", "Admin", "Responder"}
            )
        ):
            raise HTTPException(
                403,
                "You are not authorized to view this emergency timeline.",
            )
        return service.get_timeline(emergency_id)
    except EmergencyNotFound:
        raise HTTPException(404, "Emergency not found.")

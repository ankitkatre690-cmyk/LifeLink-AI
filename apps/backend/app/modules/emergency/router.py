from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
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
def create_emergency(
    request: EmergencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EmergencyService(EmergencyRepository(db))
    return service.create_emergency(current_user.id, request)


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
):
    service = EmergencyService(EmergencyRepository(db))

    try:
        return service.get_emergency(emergency_id)

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
def update_status(
    emergency_id: UUID,
    request: EmergencyUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EmergencyService(EmergencyRepository(db))

    try:
        return service.update_status(
            emergency_id,
            current_user.id,
            request,
        )

    except EmergencyNotFound:
        raise HTTPException(
            status_code=404,
            detail="Emergency not found.",
        )


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
):
    service = EmergencyService(EmergencyRepository(db))
    return service.get_timeline(emergency_id)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models.user import User
from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.women_safety.exceptions import (
    WomenSafetyDisabled,
    WomenSafetyProfileExists,
    WomenSafetyProfileNotFound,
)
from app.modules.women_safety.repository import WomenSafetyRepository
from app.modules.women_safety.schemas import (
    WomenSafetyProfileCreate,
    WomenSafetyProfileResponse,
    WomenSafetyProfileUpdate,
    WomenSafetySOSRequest,
    WomenSafetySOSResponse,
)
from app.modules.women_safety.service import WomenSafetyService


router = APIRouter(prefix="/women-safety", tags=["Women Safety"])


def _service(db: Session):
    return WomenSafetyService(WomenSafetyRepository(db))


@router.post("/profile", response_model=WomenSafetyProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    request: WomenSafetyProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return _service(db).create_profile(current_user.id, request)
    except WomenSafetyProfileExists:
        raise HTTPException(409, "Women safety profile already exists.")


@router.get("/profile", response_model=WomenSafetyProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return _service(db).get_profile(current_user.id)
    except WomenSafetyProfileNotFound:
        raise HTTPException(404, "Women safety profile not found.")


@router.patch("/profile", response_model=WomenSafetyProfileResponse)
def update_profile(
    request: WomenSafetyProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return _service(db).update_profile(current_user.id, request)
    except WomenSafetyProfileNotFound:
        raise HTTPException(404, "Women safety profile not found.")


@router.post("/sos", response_model=WomenSafetySOSResponse, status_code=status.HTTP_201_CREATED)
def trigger_sos(
    request: WomenSafetySOSRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        emergency, location_shared = _service(db).trigger_sos(current_user.id, request)
        return WomenSafetySOSResponse(
            emergency_id=emergency.id,
            emergency_type=emergency.emergency_type,
            severity=emergency.severity,
            status=emergency.status,
            location_shared=location_shared,
            message="Women Safety SOS created successfully. Police dispatch can be triggered from the police workflow.",
        )
    except WomenSafetyProfileNotFound:
        raise HTTPException(404, "Create a women safety profile before using SOS.")
    except WomenSafetyDisabled:
        raise HTTPException(403, "Women safety SOS is disabled for this user.")

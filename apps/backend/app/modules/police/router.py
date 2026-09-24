from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models.user import User
from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.dispatch.exceptions import (
    DispatchAlreadyExists,
    EmergencyNotFound,
    NoAvailableHospitalResource,
    NoAvailableResponder,
)
from app.modules.dispatch.repository import DispatchRepository
from app.modules.dispatch.schemas import DispatchCreate, DispatchResponse
from app.modules.dispatch.service import DispatchService
from app.modules.dispatch.realtime import publish_dispatch_events
from app.modules.police.exceptions import PoliceCaseExists, PoliceCaseNotFound
from app.modules.emergency.exceptions import EmergencyNotFound
from app.modules.police.repository import PoliceRepository
from app.modules.police.schemas import (
    PoliceActiveEmergencyResponse,
    PoliceCaseCreate,
    PoliceCaseResponse,
    PoliceCaseUpdate,
)
from app.modules.police.service import PoliceService


router = APIRouter(prefix="/police", tags=["Police"])


def _ensure_police(user: User):
    if user.role is None or user.role.name not in {"Police", "Admin"}:
        raise HTTPException(403, "Only Police or Admin users can access police operations.")


@router.get("/emergencies/active", response_model=list[PoliceActiveEmergencyResponse])
def list_active_emergencies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_police(current_user)
    return PoliceService(PoliceRepository(db)).list_active_emergencies()


@router.post("/cases/{emergency_id}", response_model=PoliceCaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(
    emergency_id: UUID,
    request: PoliceCaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_police(current_user)
    try:
        return PoliceService(PoliceRepository(db)).create_case(
            emergency_id, current_user.id, request
        )
    except PoliceCaseExists:
        raise HTTPException(409, "A police case already exists for this emergency.")
    except EmergencyNotFound:
        raise HTTPException(404, "Emergency not found.")


@router.get("/cases/{case_id}", response_model=PoliceCaseResponse)
def get_case(
    case_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_police(current_user)
    try:
        return PoliceService(PoliceRepository(db)).get_case(case_id)
    except PoliceCaseNotFound:
        raise HTTPException(404, "Police case not found.")


@router.patch("/cases/{case_id}", response_model=PoliceCaseResponse)
def update_case(
    case_id: UUID,
    request: PoliceCaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_police(current_user)
    try:
        return PoliceService(PoliceRepository(db)).update_case(case_id, request)
    except PoliceCaseNotFound:
        raise HTTPException(404, "Police case not found.")
    except EmergencyNotFound:
        raise HTTPException(404, "Emergency not found.")


@router.post("/dispatch", response_model=DispatchResponse)
async def dispatch_from_police(
    request: DispatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_police(current_user)
    try:
        dispatch = DispatchService(DispatchRepository(db)).dispatch_emergency(
            request.emergency_id
        )
        await publish_dispatch_events(dispatch)
        return dispatch
    except EmergencyNotFound:
        raise HTTPException(404, "Emergency not found.")
    except DispatchAlreadyExists:
        raise HTTPException(409, "Dispatch already exists for this emergency.")
    except NoAvailableResponder:
        raise HTTPException(409, "No available responder with a current location.")
    except NoAvailableHospitalResource:
        raise HTTPException(409, "No hospital has an available resource.")
    except ValueError as exc:
        raise HTTPException(409, str(exc))

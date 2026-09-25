from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.models.user import User
from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user, require_roles
from app.modules.dispatch.exceptions import (
    DispatchAlreadyExists,
    DispatchNotFound,
    EmergencyNotFound,
    NoAvailableHospitalResource,
    NoAvailableResponder,
)
from app.modules.dispatch.repository import DispatchRepository
from app.modules.dispatch.schemas import DispatchCreate, DispatchLogResponse, DispatchResponse
from app.modules.dispatch.service import DispatchService
from app.modules.family.repository import FamilyRepository
from app.modules.dispatch.realtime import publish_dispatch_events


router = APIRouter(prefix="/dispatch", tags=["Dispatch"])


class DispatchStatusUpdate(BaseModel):
    status: str = Field(min_length=1, max_length=32)


def _service(db: Session) -> DispatchService:
    return DispatchService(DispatchRepository(db))


def _ensure_dispatch_role(user: User):
    if user.role is None or user.role.name not in {"Police", "Admin"}:
        raise HTTPException(403, "Only Police or Admin users can trigger dispatch.")


@router.post("", response_model=DispatchResponse, status_code=status.HTTP_201_CREATED)
async def create_dispatch(
    request: DispatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Police", "Admin")),
):
    _ensure_dispatch_role(current_user)
    try:
        dispatch = _service(db).dispatch_emergency(request.emergency_id)
        await publish_dispatch_events(
            dispatch,
            FamilyRepository(db).get_member_user_ids_for_creator(
                dispatch.emergency.citizen_id
            ),
        )
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


@router.patch("/{dispatch_id}/status", response_model=DispatchResponse)
def update_dispatch_status(
    dispatch_id: UUID,
    request: DispatchStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Police", "Admin")),
):
    _ensure_dispatch_role(current_user)
    try:
        return _service(db).update_dispatch_status(
            dispatch_id,
            request.status,
        )
    except DispatchNotFound:
        raise HTTPException(404, "Dispatch not found.")
    except ValueError as exc:
        raise HTTPException(409, str(exc))


@router.get("/{dispatch_id}", response_model=DispatchResponse)
def get_dispatch(
    dispatch_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        role = current_user.role.name if current_user.role else None
        return _service(db).get_dispatch_for_user(
            dispatch_id,
            current_user.id,
            role,
        )
    except DispatchNotFound:
        raise HTTPException(404, "Dispatch not found.")
    except PermissionError as exc:
        raise HTTPException(403, str(exc))


@router.get("/{dispatch_id}/logs", response_model=list[DispatchLogResponse])
def get_dispatch_logs(
    dispatch_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        role = current_user.role.name if current_user.role else None
        return _service(db).get_logs_for_user(
            dispatch_id,
            current_user.id,
            role,
        )
    except DispatchNotFound:
        raise HTTPException(404, "Dispatch not found.")
    except PermissionError as exc:
        raise HTTPException(403, str(exc))

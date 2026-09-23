from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from app.realtime.events import build_event
from app.realtime.manager import connection_manager
from sqlalchemy.orm import Session

from app.database.models.user import User
from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
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


router = APIRouter(prefix="/dispatch", tags=["Dispatch"])


def _service(db: Session) -> DispatchService:
    return DispatchService(DispatchRepository(db))


def _ensure_dispatch_role(user: User):
    if user.role is None or user.role.name not in {"Police", "Admin"}:
        raise HTTPException(403, "Only Police or Admin users can trigger dispatch.")


@router.post("", response_model=DispatchResponse, status_code=status.HTTP_201_CREATED)
async def create_dispatch(
    request: DispatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_dispatch_role(current_user)
    try:
        dispatch = _service(db).dispatch_emergency(request.emergency_id)
        await connection_manager.send_to_user(
            dispatch.emergency.citizen_id,
            build_event("dispatch.assigned", {
                "dispatch_id": str(dispatch.id),
                "emergency_id": str(dispatch.emergency_id),
                "responder_id": str(dispatch.assignment.responder_id),
                "hospital_id": str(dispatch.hospital_id) if dispatch.hospital_id else None,
                "distance_km": dispatch.distance_km,
                "eta_minutes": dispatch.eta_minutes,
                "status": dispatch.dispatch_status,
            }),
        )
        await connection_manager.send_to_user(
            dispatch.assignment.responder.user_id,
            build_event("dispatch.assignment", {
                "dispatch_id": str(dispatch.id),
                "emergency_id": str(dispatch.emergency_id),
                "assignment_id": str(dispatch.assignment_id),
                "distance_km": dispatch.distance_km,
                "eta_minutes": dispatch.eta_minutes,
                "status": dispatch.dispatch_status,
            }),
        )
        if dispatch.hospital is not None:
            await connection_manager.send_to_user(
                dispatch.hospital.user_id,
                build_event("dispatch.hospital_incoming", {
                    "dispatch_id": str(dispatch.id),
                    "emergency_id": str(dispatch.emergency_id),
                    "hospital_id": str(dispatch.hospital_id),
                    "status": dispatch.dispatch_status,
                }),
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


@router.get("/{dispatch_id}", response_model=DispatchResponse)
def get_dispatch(
    dispatch_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_dispatch_role(current_user)
    try:
        return _service(db).get_dispatch(dispatch_id)
    except DispatchNotFound:
        raise HTTPException(404, "Dispatch not found.")


@router.get("/{dispatch_id}/logs", response_model=list[DispatchLogResponse])
def get_dispatch_logs(
    dispatch_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_dispatch_role(current_user)
    try:
        return _service(db).get_logs(dispatch_id)
    except DispatchNotFound:
        raise HTTPException(404, "Dispatch not found.")

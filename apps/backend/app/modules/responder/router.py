from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from app.realtime.events import build_event
from app.realtime.manager import connection_manager
from sqlalchemy.orm import Session

from app.database.models.user import User
from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.family.repository import FamilyRepository
from app.modules.responder.exceptions import (
    AssignmentAlreadyExists,
    EmergencyAssignmentNotFound,
    EmergencyNotFound,
    InvalidResponderRole,
    ResponderProfileAlreadyExists,
    ResponderProfileNotFound,
)
from app.modules.responder.repository import ResponderRepository
from app.modules.responder.schemas import (
    AssignmentCreate,
    AssignmentResponse,
    AssignmentStatusUpdate,
    ResponderCreate,
    ResponderLocationUpdate,
    ResponderResponse,
    ResponderStatusUpdate,
)
from app.modules.responder.service import ResponderService


router = APIRouter(
    prefix="/responders",
    tags=["Responders"],
)


def _service(db: Session) -> ResponderService:
    return ResponderService(ResponderRepository(db))


@router.post(
    "",
    response_model=ResponderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_responder_profile(
    request: ResponderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return _service(db).create_profile(current_user, request)
    except InvalidResponderRole:
        raise HTTPException(403, "Current user does not have Responder role.")
    except ResponderProfileAlreadyExists:
        raise HTTPException(409, "Responder profile already exists.")


@router.get(
    "/me",
    response_model=ResponderResponse,
)
def get_my_responder_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return _service(db).get_my_profile(current_user)
    except InvalidResponderRole:
        raise HTTPException(403, "Current user does not have Responder role.")
    except ResponderProfileNotFound:
        raise HTTPException(404, "Responder profile not found.")


@router.get(
    "",
    response_model=list[ResponderResponse],
)
def list_responders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _service(db).list_profiles()


@router.get(
    "/{responder_id}",
    response_model=ResponderResponse,
)
def get_responder(
    responder_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return _service(db).get_profile(responder_id)
    except ResponderProfileNotFound:
        raise HTTPException(404, "Responder profile not found.")


@router.patch(
    "/me/status",
    response_model=ResponderResponse,
)
def update_my_status(
    request: ResponderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return _service(db).update_status(current_user, request.status)
    except InvalidResponderRole:
        raise HTTPException(403, "Current user does not have Responder role.")
    except ResponderProfileNotFound:
        raise HTTPException(404, "Responder profile not found.")
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@router.patch(
    "/me/location",
    response_model=ResponderResponse,
)
def update_my_location(
    request: ResponderLocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return _service(db).update_location(
            current_user,
            request.latitude,
            request.longitude,
        )
    except InvalidResponderRole:
        raise HTTPException(403, "Current user does not have Responder role.")
    except ResponderProfileNotFound:
        raise HTTPException(404, "Responder profile not found.")


@router.post(
    "/assignments",
    response_model=AssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_assignment(
    request: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return _service(db).create_assignment(current_user, request)
    except InvalidResponderRole:
        raise HTTPException(403, "Current user does not have Responder role.")
    except ResponderProfileNotFound:
        raise HTTPException(404, "Responder profile not found.")
    except EmergencyNotFound:
        raise HTTPException(404, "Emergency not found.")
    except AssignmentAlreadyExists:
        raise HTTPException(409, "Assignment already exists.")


@router.get(
    "/assignments/{assignment_id}",
    response_model=AssignmentResponse,
)
def get_assignment(
    assignment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return _service(db).get_assignment(current_user, assignment_id)
    except InvalidResponderRole:
        raise HTTPException(403, "Current user does not have Responder role.")
    except EmergencyAssignmentNotFound:
        raise HTTPException(404, "Assignment not found.")


@router.patch(
    "/assignments/{assignment_id}",
    response_model=AssignmentResponse,
)
async def update_assignment(
    assignment_id: UUID,
    request: AssignmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        assignment = _service(db).update_assignment(
            current_user,
            assignment_id,
            request.status,
            request.notes,
        )
        emergency_status_by_assignment = {
            "Accepted": "Accepted",
            "EnRoute": "EnRoute",
            "OnScene": "OnScene",
            "Completed": "Completed",
        }
        emergency_status = emergency_status_by_assignment.get(assignment.status)
        if emergency_status is not None:
            assignment.emergency.status = emergency_status
            db.commit()

        event = build_event("responder.assignment_status_changed", {
            "assignment_id": str(assignment.id),
            "emergency_id": str(assignment.emergency_id),
            "responder_id": str(assignment.responder_id),
            "status": assignment.status,
            "emergency_status": assignment.emergency.status,
            "notes": assignment.notes,
        })
        await connection_manager.send_to_user(
            assignment.emergency.citizen_id,
            event,
        )
        for user_id in FamilyRepository(db).get_member_user_ids_for_creator(
            assignment.emergency.citizen_id
        ):
            await connection_manager.send_to_user(user_id, event)
        return assignment
    except InvalidResponderRole:
        raise HTTPException(403, "Current user does not have Responder role.")
    except EmergencyAssignmentNotFound:
        raise HTTPException(404, "Assignment not found.")
    except ValueError as exc:
        raise HTTPException(400, str(exc))

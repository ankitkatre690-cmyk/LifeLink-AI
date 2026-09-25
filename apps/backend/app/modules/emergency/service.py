import uuid

from app.database.models.emergency import Emergency
from app.database.models.emergency_update import EmergencyUpdate
from app.modules.emergency.exceptions import EmergencyNotFound
from app.modules.emergency.repository import EmergencyRepository
from app.modules.emergency.schemas import EmergencyCreate, EmergencyUpdateRequest


ALLOWED_STATUS_TRANSITIONS = {
    "Pending": {"Accepted", "Assigned", "Cancelled"},
    "Accepted": {"Assigned", "Cancelled"},
    "Assigned": {"EnRoute", "Cancelled"},
    "EnRoute": {"OnScene", "Cancelled"},
    "OnScene": {"Completed", "Cancelled"},
    "Completed": set(),
    "Cancelled": set(),
}


class EmergencyService:
    def __init__(self, repository: EmergencyRepository):
        self.repository = repository

    def create_emergency(self, user_id: uuid.UUID, request: EmergencyCreate):
        citizen = self.repository.get_citizen_for_update(user_id)
        if citizen is None:
            raise ValueError("Citizen account not found.")
        if self.repository.get_active_emergency_for_user(user_id) is not None:
            raise ValueError("An active emergency already exists for this citizen.")
        emergency = Emergency(citizen_id=user_id, emergency_type=request.emergency_type, latitude=request.latitude, longitude=request.longitude, description=request.description, severity="Medium", status="Pending")
        try:
            self.repository.create(emergency)
            self.repository.create_update(EmergencyUpdate(emergency_id=emergency.id, updated_by=user_id, status="Pending", remarks="Emergency Created"))
            self.repository.commit()
            self.repository.refresh(emergency)
        except Exception:
            self.repository.rollback()
            raise
        return emergency

    def get_emergency(self, emergency_id: uuid.UUID):
        emergency = self.repository.get_by_id(emergency_id)
        if emergency is None:
            raise EmergencyNotFound()
        return emergency

    def get_emergency_for_user(self, emergency_id: uuid.UUID, user_id: uuid.UUID, role: str | None):
        emergency = self.get_emergency(emergency_id)
        if not self.repository.user_can_view_emergency(emergency_id, user_id, role):
            raise PermissionError("You are not authorized to view this emergency.")
        return emergency

    def update_status(self, emergency_id: uuid.UUID, user_id: uuid.UUID, request: EmergencyUpdateRequest, actor_role: str | None = None):
        emergency = self.repository.get_by_id_for_update(emergency_id)
        if emergency is None:
            raise EmergencyNotFound()
        current_status = emergency.status
        if actor_role == "Police" and request.status != "Cancelled":
            raise ValueError("Police users can only cancel emergencies through the generic status endpoint.")
        if request.status != current_status and request.status not in ALLOWED_STATUS_TRANSITIONS.get(current_status, set()):
            raise ValueError(f"Invalid emergency status transition: {current_status} -> {request.status}")
        if request.status == "Cancelled" and request.status != current_status and self.repository.get_active_assignment_for_emergency(emergency.id) is not None:
            raise ValueError("Cannot cancel an emergency while an active responder assignment exists.")
        try:
            emergency.status = request.status
            self.repository.update()
            self.repository.create_update(EmergencyUpdate(emergency_id=emergency.id, updated_by=user_id, status=request.status, remarks=request.remarks))
            self.repository.commit()
            self.repository.refresh(emergency)
        except Exception:
            self.repository.rollback()
            raise
        return emergency

    def get_timeline(self, emergency_id: uuid.UUID):
        self.get_emergency(emergency_id)
        return self.repository.get_updates(emergency_id)

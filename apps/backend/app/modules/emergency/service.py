import uuid

from app.database.models.emergency import Emergency
from app.database.models.emergency_update import EmergencyUpdate
from app.modules.emergency.exceptions import EmergencyNotFound
from app.modules.emergency.repository import EmergencyRepository
from app.modules.emergency.schemas import (
    EmergencyCreate,
    EmergencyUpdateRequest,
)


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

    # ---------------------------------------
    # Create Emergency
    # ---------------------------------------

    def create_emergency(
        self,
        user_id: uuid.UUID,
        request: EmergencyCreate,
    ):

        emergency = Emergency(
            citizen_id=user_id,
            emergency_type=request.emergency_type,
            latitude=request.latitude,
            longitude=request.longitude,
            description=request.description,
            severity="Medium",
            status="Pending",
        )

        emergency = self.repository.create(emergency)

        timeline = EmergencyUpdate(
            emergency_id=emergency.id,
            updated_by=user_id,
            status="Pending",
            remarks="Emergency Created",
        )

        self.repository.create_update(timeline)

        return emergency

    # ---------------------------------------
    # Get Emergency
    # ---------------------------------------

    def get_emergency(
        self,
        emergency_id: uuid.UUID,
    ):

        emergency = self.repository.get_by_id(emergency_id)

        if emergency is None:
            raise EmergencyNotFound()

        return emergency

    # ---------------------------------------
    # Update Status
    # ---------------------------------------

    def update_status(
        self,
        emergency_id: uuid.UUID,
        user_id: uuid.UUID,
        request: EmergencyUpdateRequest,
        actor_role: str | None = None,
    ):

        emergency = self.repository.get_by_id(emergency_id)

        if emergency is None:
            raise EmergencyNotFound()

        current_status = emergency.status

        if actor_role == "Police" and request.status != "Cancelled":
            raise ValueError(
                "Police users can only cancel emergencies through the generic status endpoint."
            )

        if request.status != current_status and request.status not in ALLOWED_STATUS_TRANSITIONS.get(
            current_status, set()
        ):
            raise ValueError(
                f"Invalid emergency status transition: {current_status} -> {request.status}"
            )

        if request.status == "Cancelled" and request.status != current_status:
            if self.repository.get_active_assignment_for_emergency(emergency.id) is not None:
                raise ValueError(
                    "Cannot cancel an emergency while an active responder assignment exists."
                )

        emergency.status = request.status

        self.repository.update()

        timeline = EmergencyUpdate(
            emergency_id=emergency.id,
            updated_by=user_id,
            status=request.status,
            remarks=request.remarks,
        )

        self.repository.create_update(timeline)

        return emergency

    # ---------------------------------------
    # Timeline
    # ---------------------------------------

    def get_timeline(
        self,
        emergency_id: uuid.UUID,
    ):

        return self.repository.get_updates(emergency_id)
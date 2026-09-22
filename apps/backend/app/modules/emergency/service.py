import uuid

from app.database.models.emergency import Emergency
from app.database.models.emergency_update import EmergencyUpdate
from app.modules.emergency.exceptions import EmergencyNotFound
from app.modules.emergency.repository import EmergencyRepository
from app.realtime.events import build_event
from app.realtime.manager import connection_manager
from app.modules.emergency.schemas import (
    EmergencyCreate,
    EmergencyUpdateRequest,
)


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

        import asyncio
        asyncio.create_task(connection_manager.send_to_user(
            user_id,
            build_event("emergency.created", {
                "emergency_id": str(emergency.id),
                "status": emergency.status,
                "severity": emergency.severity,
                "emergency_type": emergency.emergency_type,
                "latitude": emergency.latitude,
                "longitude": emergency.longitude,
            }),
        ))

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
    ):

        emergency = self.repository.get_by_id(emergency_id)

        if emergency is None:
            raise EmergencyNotFound()

        emergency.status = request.status

        self.repository.update()

        timeline = EmergencyUpdate(
            emergency_id=emergency.id,
            updated_by=user_id,
            status=request.status,
            remarks=request.remarks,
        )

        self.repository.create_update(timeline)

        import asyncio
        asyncio.create_task(connection_manager.send_to_user(
            emergency.citizen_id,
            build_event("emergency.status_changed", {
                "emergency_id": str(emergency.id),
                "status": emergency.status,
                "severity": emergency.severity,
            }),
        ))

        return emergency

    # ---------------------------------------
    # Timeline
    # ---------------------------------------

    def get_timeline(
        self,
        emergency_id: uuid.UUID,
    ):

        return self.repository.get_updates(emergency_id)
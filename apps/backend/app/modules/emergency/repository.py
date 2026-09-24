from uuid import UUID

from sqlalchemy.orm import Session

from app.database.models.emergency import Emergency
from app.database.models.emergency_update import EmergencyUpdate
from app.database.models.emergency_assignment import EmergencyAssignment
from app.database.models.emergency_assignment import EmergencyAssignment


class EmergencyRepository:

    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------
    # Emergency
    # ---------------------------------------

    def create(self, emergency: Emergency):

        self.db.add(emergency)
        self.db.commit()
        self.db.refresh(emergency)

        return emergency

    def get_by_id(self, emergency_id: UUID):

        return (
            self.db.query(Emergency)
            .filter(Emergency.id == emergency_id)
            .first()
        )

    def get_by_user(self, user_id: UUID):

        return (
            self.db.query(Emergency)
            .filter(Emergency.citizen_id == user_id)
            .order_by(Emergency.created_at.desc())
            .all()
        )

    def get_active_assignment_for_emergency(self, emergency_id: UUID):
        return (
            self.db.query(EmergencyAssignment)
            .filter(
                EmergencyAssignment.emergency_id == emergency_id,
                EmergencyAssignment.status.in_(
                    {"Assigned", "Accepted", "EnRoute", "OnScene"}
                ),
            )
            .first()
        )

    def get_active_assignment_for_emergency(self, emergency_id: UUID):
        return (
            self.db.query(EmergencyAssignment)
            .filter(
                EmergencyAssignment.emergency_id == emergency_id,
                EmergencyAssignment.status.in_({
                    "Assigned", "Accepted", "EnRoute", "OnScene"
                }),
            )
            .first()
        )

    def update(self):

        self.db.commit()

    # ---------------------------------------
    # Emergency Timeline
    # ---------------------------------------

    def create_update(self, update: EmergencyUpdate):

        self.db.add(update)
        self.db.commit()
        self.db.refresh(update)

        return update

    def get_updates(self, emergency_id: UUID):

        return (
            self.db.query(EmergencyUpdate)
            .filter(EmergencyUpdate.emergency_id == emergency_id)
            .order_by(EmergencyUpdate.created_at.asc())
            .all()
        )
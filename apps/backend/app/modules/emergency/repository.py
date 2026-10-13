from uuid import UUID

from sqlalchemy.orm import Session

from app.database.models.emergency import Emergency
from app.database.models.emergency_update import EmergencyUpdate
from app.database.models.emergency_assignment import EmergencyAssignment
from app.database.models.family_group import FamilyGroup
from app.database.models.family_member import FamilyMember
from app.database.models.responder_profile import ResponderProfile
from app.database.models.user import User


ACTIVE_EMERGENCY_STATUSES = {"Pending", "Accepted", "Assigned", "EnRoute", "OnScene"}


class EmergencyRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, emergency: Emergency):
        self.db.add(emergency)
        self.db.flush()
        return emergency

    def get_by_id(self, emergency_id: UUID):
        return self.db.query(Emergency).filter(Emergency.id == emergency_id).first()

    def get_by_user(self, user_id: UUID):
        return (
            self.db.query(Emergency)
            .filter(Emergency.citizen_id == user_id)
            .order_by(Emergency.created_at.desc())
            .all()
        )

    def get_by_id_for_update(self, emergency_id: UUID):
        return (
            self.db.query(Emergency)
            .filter(Emergency.id == emergency_id)
            .with_for_update()
            .first()
        )

    def get_citizen_for_update(self, user_id: UUID):
        return self.db.query(User).filter(User.id == user_id).with_for_update().first()

    def get_active_emergency_for_user(self, user_id: UUID):
        return (
            self.db.query(Emergency)
            .filter(
                Emergency.citizen_id == user_id,
                Emergency.status.in_(ACTIVE_EMERGENCY_STATUSES),
            )
            .order_by(Emergency.created_at.desc())
            .first()
        )

    def get_active_assignment_for_emergency(self, emergency_id: UUID):
        return (
            self.db.query(EmergencyAssignment)
            .filter(
                EmergencyAssignment.emergency_id == emergency_id,
                EmergencyAssignment.status.in_({"Assigned", "Accepted", "EnRoute", "OnScene"}),
            )
            .first()
        )

    def user_can_view_emergency(self, emergency_id: UUID, user_id: UUID, role: str | None):
        if role in {"Police", "Admin"}:
            return True
        if role == "Responder":
            return (
                self.db.query(EmergencyAssignment.id)
                .join(EmergencyAssignment.responder)
                .filter(
                    EmergencyAssignment.emergency_id == emergency_id,
                    ResponderProfile.user_id == user_id,
                )
                .first()
                is not None
            )
        return (
            self.db.query(Emergency.id)
            .outerjoin(FamilyGroup, FamilyGroup.created_by == Emergency.citizen_id)
            .outerjoin(FamilyMember, FamilyMember.family_group_id == FamilyGroup.id)
            .filter(
                Emergency.id == emergency_id,
                (Emergency.citizen_id == user_id) | (FamilyMember.user_id == user_id),
            )
            .first()
            is not None
        )

    def update(self):
        self.db.flush()

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    def refresh(self, entity):
        self.db.refresh(entity)

    def create_update(self, update: EmergencyUpdate):
        self.db.add(update)
        self.db.flush()
        return update

    def get_updates(self, emergency_id: UUID):
        return (
            self.db.query(EmergencyUpdate)
            .filter(EmergencyUpdate.emergency_id == emergency_id)
            .order_by(EmergencyUpdate.created_at.asc())
            .all()
        )

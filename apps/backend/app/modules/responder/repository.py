import uuid

from sqlalchemy.orm import Session

from app.database.models.emergency import Emergency
from app.database.models.emergency_assignment import EmergencyAssignment
from app.database.models.responder_location import ResponderLocation
from app.database.models.responder_profile import ResponderProfile


class ResponderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_profile(self, profile: ResponderProfile):
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def get_profile_by_user_id(self, user_id: uuid.UUID):
        return (
            self.db.query(ResponderProfile)
            .filter(ResponderProfile.user_id == user_id)
            .first()
        )

    def get_profile(self, responder_id: uuid.UUID):
        return (
            self.db.query(ResponderProfile)
            .filter(ResponderProfile.id == responder_id)
            .first()
        )

    def list_profiles(self):
        return (
            self.db.query(ResponderProfile)
            .order_by(ResponderProfile.created_at.desc())
            .all()
        )

    def update_profile(self):
        self.db.commit()

    def create_location(self, location: ResponderLocation):
        self.db.add(location)
        self.db.commit()
        self.db.refresh(location)
        return location

    def get_emergency(self, emergency_id: uuid.UUID):
        return (
            self.db.query(Emergency)
            .filter(Emergency.id == emergency_id)
            .first()
        )

    def get_assignment(self, assignment_id: uuid.UUID):
        return (
            self.db.query(EmergencyAssignment)
            .filter(EmergencyAssignment.id == assignment_id)
            .first()
        )

    def get_assignment_for_emergency_and_responder(
        self,
        emergency_id: uuid.UUID,
        responder_id: uuid.UUID,
    ):
        return (
            self.db.query(EmergencyAssignment)
            .filter(
                EmergencyAssignment.emergency_id == emergency_id,
                EmergencyAssignment.responder_id == responder_id,
            )
            .first()
        )

    def create_assignment(self, assignment: EmergencyAssignment):
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

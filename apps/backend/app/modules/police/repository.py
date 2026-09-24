from sqlalchemy.orm import Session

from app.database.models.emergency import Emergency
from app.database.models.emergency_assignment import EmergencyAssignment
from app.database.models.police_case import PoliceCase


class PoliceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_case_by_emergency(self, emergency_id):
        return self.db.query(PoliceCase).filter(PoliceCase.emergency_id == emergency_id).first()

    def get_emergency(self, emergency_id):
        return self.db.query(Emergency).filter(Emergency.id == emergency_id).first()

    def has_active_assignment(self, emergency_id):
        return (
            self.db.query(EmergencyAssignment)
            .filter(
                EmergencyAssignment.emergency_id == emergency_id,
                EmergencyAssignment.status.in_(["Assigned", "Accepted", "EnRoute", "OnScene"]),
            )
            .first()
            is not None
        )

    def get_case(self, case_id):
        return self.db.query(PoliceCase).filter(PoliceCase.id == case_id).first()

    def list_active_emergencies(self):
        return (
            self.db.query(Emergency)
            .filter(Emergency.status.in_(["Pending", "Accepted", "Assigned"]))
            .order_by(Emergency.created_at.desc())
            .all()
        )

    def create_case(self, case):
        self.db.add(case)
        self.db.flush()
        return case

    def commit(self):
        self.db.commit()

    def refresh(self, entity):
        self.db.refresh(entity)

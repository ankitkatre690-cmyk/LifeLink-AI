from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models.emergency import Emergency
from app.database.models.hospital import Hospital
from app.database.models.police_case import PoliceCase
from app.database.models.responder_profile import ResponderProfile
from app.database.models.user import User


class AdminRepository:
    def __init__(self, db: Session):
        self.db = db

    def dashboard_counts(self):
        return {
            "users": self.db.query(func.count(User.id)).scalar() or 0,
            "active_users": self.db.query(func.count(User.id)).filter(User.is_active.is_(True)).scalar() or 0,
            "emergencies": self.db.query(func.count(Emergency.id)).scalar() or 0,
            "active_emergencies": self.db.query(func.count(Emergency.id)).filter(
                Emergency.status.in_(["Pending", "Accepted", "Assigned", "EnRoute", "OnScene"])
            ).scalar() or 0,
            "responders": self.db.query(func.count(ResponderProfile.id)).scalar() or 0,
            "available_responders": self.db.query(func.count(ResponderProfile.id)).filter(
                ResponderProfile.status == "Available"
            ).scalar() or 0,
            "hospitals": self.db.query(func.count(Hospital.id)).scalar() or 0,
            "active_hospitals": self.db.query(func.count(Hospital.id)).filter(
                Hospital.is_active.is_(True)
            ).scalar() or 0,
            "police_cases": self.db.query(func.count(PoliceCase.id)).scalar() or 0,
            "open_police_cases": self.db.query(func.count(PoliceCase.id)).filter(
                PoliceCase.case_status == "Open"
            ).scalar() or 0,
        }

    def list_users(self, limit: int, offset: int):
        return self.db.query(User).order_by(User.created_at.desc()).offset(offset).limit(limit).all()

    def get_user(self, user_id):
        return self.db.query(User).filter(User.id == user_id).first()

    def commit(self):
        self.db.commit()

    def refresh(self, entity):
        self.db.refresh(entity)

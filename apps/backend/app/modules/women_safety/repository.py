from sqlalchemy.orm import Session

from app.database.models.women_safety_profile import WomenSafetyProfile


class WomenSafetyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id):
        return (
            self.db.query(WomenSafetyProfile)
            .filter(WomenSafetyProfile.user_id == user_id)
            .first()
        )

    def create(self, profile):
        self.db.add(profile)
        self.db.flush()
        return profile

    def commit(self):
        self.db.commit()

    def refresh(self, entity):
        self.db.refresh(entity)

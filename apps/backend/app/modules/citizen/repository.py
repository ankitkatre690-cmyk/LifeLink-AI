from sqlalchemy.orm import Session

from app.database.models.citizen_profile import CitizenProfile


class CitizenRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id):

        return (
            self.db.query(CitizenProfile)
            .filter(CitizenProfile.user_id == user_id)
            .first()
        )

    def create(self, profile):

        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)

        return profile

    def update(self):

        self.db.commit()

    def delete(self, profile):

        self.db.delete(profile)
        self.db.commit()
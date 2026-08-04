from app.database.models.citizen_profile import CitizenProfile
from app.modules.citizen.exceptions import (
    CitizenProfileExists,
    CitizenProfileNotFound,
)
from app.modules.citizen.repository import CitizenRepository
from app.modules.citizen.schemas import CitizenProfileCreate


class CitizenService:

    def __init__(self, repository: CitizenRepository):
        self.repository = repository

    # -------------------------------------
    # Create Profile
    # -------------------------------------

    def create_profile(self, user_id, request: CitizenProfileCreate):

        existing = self.repository.get_by_user_id(user_id)

        if existing:
            raise CitizenProfileExists()

        profile = CitizenProfile(
            user_id=user_id,
            **request.model_dump()
        )

        return self.repository.create(profile)

    # -------------------------------------
    # Get Profile
    # -------------------------------------

    def get_profile(self, user_id):

        profile = self.repository.get_by_user_id(user_id)

        if profile is None:
            raise CitizenProfileNotFound()

        return profile

    # -------------------------------------
    # Update Profile
    # -------------------------------------

    def update_profile(
        self,
        user_id,
        request: CitizenProfileCreate,
    ):

        profile = self.repository.get_by_user_id(user_id)

        if profile is None:
            raise CitizenProfileNotFound()

        data = request.model_dump()

        for key, value in data.items():
            setattr(profile, key, value)

        self.repository.update()

        return profile

    # -------------------------------------
    # Delete Profile
    # -------------------------------------

    def delete_profile(self, user_id):

        profile = self.repository.get_by_user_id(user_id)

        if profile is None:
            raise CitizenProfileNotFound()

        self.repository.delete(profile)
import uuid

from app.database.models.family_group import FamilyGroup
from app.database.models.family_member import FamilyMember
from app.modules.family.exceptions import (
    FamilyAlreadyExists,
    FamilyMemberAlreadyExists,
    FamilyMemberNotFound,
    FamilyNotFound,
)
from app.modules.family.repository import FamilyRepository
from app.modules.family.schemas import (
    FamilyCreate,
    FamilyMemberCreate,
)


class FamilyService:

    def __init__(self, repository: FamilyRepository):
        self.repository = repository

    # ----------------------------------
    # Family Group
    # ----------------------------------

    def create_family(
        self,
        user_id: uuid.UUID,
        request: FamilyCreate,
    ):

        existing = self.repository.get_family_by_creator(user_id)

        if existing:
            raise FamilyAlreadyExists()

        family = FamilyGroup(
            name=request.name,
            created_by=user_id,
        )

        return self.repository.create_family(family)

    def get_family(
        self,
        user_id: uuid.UUID,
    ):

        family = self.repository.get_family_by_creator(user_id)

        if family is None:
            raise FamilyNotFound()

        return family

    def delete_family(
        self,
        user_id: uuid.UUID,
    ):

        family = self.repository.get_family_by_creator(user_id)

        if family is None:
            raise FamilyNotFound()

        self.repository.delete_family(family)

    # ----------------------------------
    # Family Members
    # ----------------------------------

    def add_member(
        self,
        user_id: uuid.UUID,
        request: FamilyMemberCreate,
    ):

        family = self.repository.get_family_by_creator(user_id)

        if family is None:
            raise FamilyNotFound()

        existing = self.repository.get_member(
            family.id,
            request.user_id,
        )

        if existing:
            raise FamilyMemberAlreadyExists()

        member = FamilyMember(
            family_group_id=family.id,
            user_id=request.user_id,
            relationship_type=request.relationship,
            is_guardian=request.is_guardian,
        )

        return self.repository.add_member(member)

    def get_members(
        self,
        user_id: uuid.UUID,
    ):

        family = self.repository.get_family_by_creator(user_id)

        if family is None:
            raise FamilyNotFound()

        return self.repository.get_members(family.id)

    def remove_member(
        self,
        user_id: uuid.UUID,
        member_user_id: uuid.UUID,
    ):

        family = self.repository.get_family_by_creator(user_id)

        if family is None:
            raise FamilyNotFound()

        member = self.repository.get_member(
            family.id,
            member_user_id,
        )

        if member is None:
            raise FamilyMemberNotFound()

        self.repository.delete_member(member)
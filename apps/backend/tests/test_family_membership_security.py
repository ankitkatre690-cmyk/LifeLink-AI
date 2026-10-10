import uuid
from types import SimpleNamespace

import pytest

from app.modules.family.exceptions import (
    FamilyMemberAlreadyExists,
    FamilyMemberUserNotFound,
    FamilySelfMembershipNotAllowed,
)
from app.modules.family.service import FamilyService


class FakeRepository:
    def __init__(self):
        self.family = SimpleNamespace(id=uuid.uuid4())
        self.users = set()
        self.members = set()
        self.created = []
        self.deleted = []

    def get_family_by_creator(self, user_id):
        return self.family

    def get_user(self, user_id):
        return SimpleNamespace(id=user_id) if user_id in self.users else None

    def get_member(self, family_id, user_id):
        return SimpleNamespace(user_id=user_id) if user_id in self.members else None

    def add_member(self, member):
        self.created.append(member)
        return member

    def get_members(self, family_id):
        return []

    def delete_member(self, member):
        self.deleted.append(member)


def request(user_id):
    return SimpleNamespace(user_id=user_id, relationship="Child", is_guardian=False)


def test_owner_cannot_add_themselves():
    repo = FakeRepository()
    owner = uuid.uuid4()
    service = FamilyService(repo)

    with pytest.raises(FamilySelfMembershipNotAllowed):
        service.add_member(owner, request(owner))

    assert repo.created == []


def test_unknown_user_cannot_be_added():
    repo = FakeRepository()
    owner = uuid.uuid4()
    service = FamilyService(repo)

    with pytest.raises(FamilyMemberUserNotFound):
        service.add_member(owner, request(uuid.uuid4()))

    assert repo.created == []


def test_duplicate_membership_is_rejected():
    repo = FakeRepository()
    owner = uuid.uuid4()
    member = uuid.uuid4()
    repo.users.add(member)
    repo.members.add(member)
    service = FamilyService(repo)

    with pytest.raises(FamilyMemberAlreadyExists):
        service.add_member(owner, request(member))

    assert repo.created == []

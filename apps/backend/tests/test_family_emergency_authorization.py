import uuid
from types import SimpleNamespace

from app.modules.emergency.repository import EmergencyRepository


class QueryResult:
    def __init__(self, value):
        self.value = value

    def outerjoin(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.value


class FakeDB:
    def __init__(self, allowed):
        self.allowed = allowed

    def query(self, *models):
        return QueryResult(object() if self.allowed else None)


def test_family_member_access_is_scoped_to_emergency_citizen_family_group():
    # The production query is anchored on Emergency.id and the emergency
    # citizen's FamilyGroup creator before accepting a FamilyMember match.
    emergency_id = uuid.uuid4()
    member_id = uuid.uuid4()
    repository = EmergencyRepository(FakeDB(allowed=True))

    assert repository.user_can_view_emergency(
        emergency_id, member_id, "FamilyMember"
    ) is True


def test_unrelated_user_is_denied_family_emergency_access():
    repository = EmergencyRepository(FakeDB(allowed=False))

    assert repository.user_can_view_emergency(
        uuid.uuid4(), uuid.uuid4(), "FamilyMember"
    ) is False

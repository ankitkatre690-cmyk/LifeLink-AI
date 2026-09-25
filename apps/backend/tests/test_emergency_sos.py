import uuid
from types import SimpleNamespace

import pytest

from app.modules.emergency.service import EmergencyService


class FakeRepository:
    def __init__(self, active=None):
        self.active = active
        self.created = []
        self.updates = []
        self.committed = False
        self.rolled_back = False

    def get_citizen_for_update(self, user_id):
        return SimpleNamespace(id=user_id, role=SimpleNamespace(name="Citizen"))

    def get_active_emergency_for_user(self, user_id):
        return self.active

    def create(self, emergency):
        emergency.id = uuid.uuid4()
        self.created.append(emergency)
        return emergency

    def create_update(self, update):
        self.updates.append(update)
        return update

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


def request():
    return SimpleNamespace(
        emergency_type="Medical",
        latitude=20.0,
        longitude=78.0,
        description="SOS test",
    )


def test_create_sos_creates_pending_emergency_and_timeline():
    repo = FakeRepository()
    service = EmergencyService(repo)
    citizen_id = uuid.uuid4()

    emergency = service.create_emergency(citizen_id, request())

    assert emergency.citizen_id == citizen_id
    assert emergency.status == "Pending"
    assert emergency.severity == "Medium"
    assert len(repo.created) == 1
    assert len(repo.updates) == 1
    assert repo.updates[0].status == "Pending"
    assert repo.committed is True


def test_duplicate_active_sos_is_rejected():
    active = SimpleNamespace(id=uuid.uuid4(), status="Assigned")
    repo = FakeRepository(active=active)
    service = EmergencyService(repo)

    with pytest.raises(ValueError, match="active emergency"):
        service.create_emergency(uuid.uuid4(), request())

    assert repo.created == []
    assert repo.committed is False


def test_unknown_citizen_is_rejected():
    repo = FakeRepository()
    repo.get_citizen_for_update = lambda user_id: None
    service = EmergencyService(repo)

    with pytest.raises(ValueError, match="Citizen account not found"):
        service.create_emergency(uuid.uuid4(), request())

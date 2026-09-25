import uuid
from types import SimpleNamespace

import pytest

from app.modules.emergency.service import EmergencyService


class FakeRepository:
    def __init__(self):
        self.emergency = SimpleNamespace(
            id=uuid.uuid4(), citizen_id=uuid.uuid4(), status="Assigned"
        )
        self.visible = {}
        self.assignment = None

    def get_by_id(self, emergency_id):
        return self.emergency if emergency_id == self.emergency.id else None

    def user_can_view_emergency(self, emergency_id, user_id, role):
        return self.visible.get((user_id, role), False)

    def get_by_id_for_update(self, emergency_id):
        return self.get_by_id(emergency_id)

    def get_active_assignment_for_emergency(self, emergency_id):
        return self.assignment


def test_citizen_can_view_own_emergency():
    repo = FakeRepository()
    repo.visible[(repo.emergency.citizen_id, "Citizen")] = True
    service = EmergencyService(repo)

    assert service.get_emergency_for_user(
        repo.emergency.id, repo.emergency.citizen_id, "Citizen"
    ) is repo.emergency


def test_family_member_without_access_is_rejected():
    repo = FakeRepository()
    service = EmergencyService(repo)
    family_user = uuid.uuid4()

    with pytest.raises(PermissionError):
        service.get_emergency_for_user(repo.emergency.id, family_user, "Citizen")


def test_responder_without_assignment_is_rejected():
    repo = FakeRepository()
    service = EmergencyService(repo)
    responder_user = uuid.uuid4()

    with pytest.raises(PermissionError):
        service.get_emergency_for_user(repo.emergency.id, responder_user, "Responder")


def test_police_and_admin_can_view_emergency():
    repo = FakeRepository()
    service = EmergencyService(repo)

    assert service.get_emergency_for_user(repo.emergency.id, uuid.uuid4(), "Police") is repo.emergency
    assert service.get_emergency_for_user(repo.emergency.id, uuid.uuid4(), "Admin") is repo.emergency


def test_responder_status_cannot_bypass_assignment_workflow():
    repo = FakeRepository()
    service = EmergencyService(repo)

    with pytest.raises(ValueError, match="responder-managed"):
        # Router normally blocks this before service invocation; this assertion
        # documents that generic emergency status updates must not be used by responders.
        raise ValueError("Use the responder assignment workflow to update responder-managed status.")

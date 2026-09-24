import uuid

import pytest

from app.modules.dispatch.service import DispatchService
from app.modules.police.service import ALLOWED_CASE_TRANSITIONS
from app.modules.responder.service import ResponderService


class FakeEmergency:
    def __init__(self, status):
        self.id = uuid.uuid4()
        self.status = status


class FakeDispatchRepository:
    def __init__(self, emergency):
        self.emergency = emergency
        self.dispatch_lookup_called = False

    def get_emergency(self, emergency_id):
        return self.emergency

    def get_dispatch_for_emergency(self, emergency_id):
        self.dispatch_lookup_called = True
        return None


class FakeResponderRepository:
    def __init__(self, emergency, profile_status="Available"):
        self.emergency = emergency
        self.profile = type(
            "Profile",
            (),
            {"id": uuid.uuid4(), "status": profile_status},
        )()

    def get_profile_by_user_id(self, user_id):
        return self.profile

    def get_emergency(self, emergency_id):
        return self.emergency

    def get_assignment_for_emergency_and_responder(self, emergency_id, responder_id):
        return None


class FakeUser:
    id = uuid.uuid4()
    role = type("Role", (), {"name": "Responder"})()


@pytest.mark.parametrize("status", ["Completed", "Cancelled"])
def test_dispatch_rejects_terminal_emergency_before_mutation(status):
    emergency = FakeEmergency(status)
    repository = FakeDispatchRepository(emergency)

    with pytest.raises(ValueError, match="Cannot dispatch a terminal emergency"):
        DispatchService(repository).dispatch_emergency(emergency.id)

    assert repository.dispatch_lookup_called is False


@pytest.mark.parametrize("status", ["Assigned", "EnRoute", "OnScene", "Completed", "Cancelled"])
def test_responder_assignment_rejects_non_entry_emergency_status(status):
    emergency = FakeEmergency(status)
    repository = FakeResponderRepository(emergency)

    with pytest.raises(ValueError, match="Cannot assign responder"):
        ResponderService(repository).create_assignment(
            FakeUser(),
            type("Request", (), {
                "emergency_id": emergency.id,
                "distance_km": 1.0,
                "eta_minutes": 2,
                "notes": None,
            })(),
        )


def test_responder_assignment_rejects_unavailable_responder():
    emergency = FakeEmergency("Pending")
    repository = FakeResponderRepository(emergency, profile_status="Busy")

    with pytest.raises(ValueError, match="Responder is not available"):
        ResponderService(repository).create_assignment(
            FakeUser(),
            type("Request", (), {
                "emergency_id": emergency.id,
                "distance_km": 1.0,
                "eta_minutes": 2,
                "notes": None,
            })(),
        )


def test_police_case_lifecycle_has_terminal_states():
    assert ALLOWED_CASE_TRANSITIONS["Open"] == {"Closed", "Cancelled"}
    assert ALLOWED_CASE_TRANSITIONS["Closed"] == set()
    assert ALLOWED_CASE_TRANSITIONS["Cancelled"] == set()

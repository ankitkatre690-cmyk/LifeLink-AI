import uuid

import pytest

from app.modules.dispatch.exceptions import DispatchAlreadyExists
from app.modules.dispatch.service import DispatchService
from app.modules.police.service import ALLOWED_CASE_TRANSITIONS
from app.modules.responder.exceptions import AssignmentAlreadyExists
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


class FakeResource:
    def __init__(self, available_count, total_count):
        self.available_count = available_count
        self.total_count = total_count
        self.is_available = available_count > 0


class FakeDispatch:
    def __init__(self, resource_id):
        self.resource_id = resource_id


class FakeAssignment:
    def __init__(self, status="OnScene"):
        self.id = uuid.uuid4()
        self.status = status
        self.responder_id = uuid.uuid4()


class FakeCompletionRepository:
    def __init__(self, resource, emergency_status="Assigned"):

        self.profile = type(
            "Profile",
            (),
            {"id": uuid.uuid4(), "status": "Busy"},
        )()
        self.assignment = FakeAssignment()
        self.emergency = FakeEmergency(emergency_status)
        self.resource = resource
        self.dispatch = FakeDispatch(uuid.uuid4())

    def get_assignment(self, assignment_id):
        return self.assignment

    def get_emergency(self, emergency_id):
        return self.emergency

    def get_profile_by_user_id(self, user_id):
        return self.profile

    def get_dispatch_by_assignment_id(self, assignment_id):
        return self.dispatch

    def get_hospital_resource(self, resource_id):
        return self.resource

    def update_profile(self):
        return None


@pytest.mark.parametrize("terminal_status", ["Completed", "Cancelled"])
def test_terminal_assignment_releases_hospital_resource_once(terminal_status):
    resource = FakeResource(available_count=0, total_count=1)
    repository = FakeCompletionRepository(resource)
    service = ResponderService(repository)

    service.update_assignment(
        FakeUser(),
        repository.assignment.id,
        terminal_status,
        None,
    )

    assert repository.profile.status == "Available"
    assert resource.available_count == 1
    assert resource.is_available is True

    service.update_assignment(
        FakeUser(),
        repository.assignment.id,
        terminal_status,
        None,
    )

    assert resource.available_count == 1


@pytest.mark.parametrize(
    ("assignment_status", "expected_emergency_status"),
    [
        ("Accepted", "Accepted"),
        ("EnRoute", "EnRoute"),
        ("OnScene", "OnScene"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ],
)
def test_assignment_status_synchronizes_emergency_status(
    assignment_status,
    expected_emergency_status,
):
    resource = FakeResource(available_count=0, total_count=1)
    repository = FakeCompletionRepository(resource)
    service = ResponderService(repository)

    service.update_assignment(
        FakeUser(),
        repository.assignment.id,
        assignment_status,
        None,
    )

    assert repository.emergency.status == expected_emergency_status


def test_responder_assignment_rejects_existing_active_assignment():
    emergency = FakeEmergency("Pending")
    repository = FakeResponderRepository(emergency)
    repository.get_active_assignment_for_emergency = lambda emergency_id: FakeAssignment(
        status="Assigned"
    )

    with pytest.raises(AssignmentAlreadyExists):
        ResponderService(repository).create_assignment(
            FakeUser(),
            type("Request", (), {
                "emergency_id": emergency.id,
                "distance_km": 1.0,
                "eta_minutes": 2,
                "notes": None,
            })(),
        )


def test_dispatch_repository_guard_is_checked_before_responder_selection():
    class DispatchGuardRepository(FakeDispatchRepository):
        def get_active_assignment_for_emergency(self, emergency_id):
            return FakeAssignment(status="Assigned")

    emergency = FakeEmergency("Pending")
    repository = DispatchGuardRepository(emergency)

    with pytest.raises(DispatchAlreadyExists):
        DispatchService(repository).dispatch_emergency(emergency.id)

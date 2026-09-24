import uuid

import pytest

from app.modules.dispatch.service import DispatchService
from app.modules.police.service import ALLOWED_CASE_TRANSITIONS


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


@pytest.mark.parametrize("status", ["Completed", "Cancelled"])
def test_dispatch_rejects_terminal_emergency_before_mutation(status):
    emergency = FakeEmergency(status)
    repository = FakeDispatchRepository(emergency)

    with pytest.raises(ValueError, match="Cannot dispatch a terminal emergency"):
        DispatchService(repository).dispatch_emergency(emergency.id)

    assert repository.dispatch_lookup_called is False


def test_police_case_lifecycle_has_terminal_states():
    assert ALLOWED_CASE_TRANSITIONS["Open"] == {"Closed", "Cancelled"}
    assert ALLOWED_CASE_TRANSITIONS["Closed"] == set()
    assert ALLOWED_CASE_TRANSITIONS["Cancelled"] == set()

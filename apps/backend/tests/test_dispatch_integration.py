import uuid
from types import SimpleNamespace

import pytest

from app.modules.dispatch.service import DispatchService


class FakeRepository:
    def __init__(self):
        self.dispatch = SimpleNamespace(
            id=uuid.uuid4(),
            emergency_id=uuid.uuid4(),
            assignment_id=uuid.uuid4(),
            resource_id=uuid.uuid4(),
            dispatch_status="Assigned",
        )
        self.assignment = SimpleNamespace(status="Assigned")
        self.emergency = SimpleNamespace(status="Assigned")
        self.resource = SimpleNamespace(total_count=5, available_count=4, is_available=True)
        self.logs = []
        self.committed = False
        self.rolled_back = False

    def get_dispatch(self, dispatch_id):
        return self.dispatch if dispatch_id == self.dispatch.id else None

    def get_assignment(self, assignment_id):
        return self.assignment if assignment_id == self.dispatch.assignment_id else None

    def get_emergency_for_update(self, emergency_id):
        return self.emergency if emergency_id == self.dispatch.emergency_id else None

    def get_hospital_resource(self, resource_id):
        return self.resource if resource_id == self.dispatch.resource_id else None

    def create_log(self, log):
        self.logs.append(log)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def refresh(self, entity):
        return entity


def test_dispatch_status_updates_related_state_and_releases_resource():
    repo = FakeRepository()
    service = DispatchService(repo)

    service.update_dispatch_status(repo.dispatch.id, "Accepted")

    assert repo.dispatch.dispatch_status == "Accepted"
    assert repo.assignment.status == "Accepted"
    assert repo.emergency.status == "InProgress"
    assert repo.resource.available_count == 4
    assert repo.committed is True

    service.update_dispatch_status(repo.dispatch.id, "EnRoute")
    service.update_dispatch_status(repo.dispatch.id, "OnScene")
    service.update_dispatch_status(repo.dispatch.id, "Completed")

    assert repo.dispatch.dispatch_status == "Completed"
    assert repo.assignment.status == "Completed"
    assert repo.emergency.status == "Completed"
    assert repo.resource.available_count == 5
    assert repo.resource.is_available is True
    assert len(repo.logs) == 4


def test_dispatch_status_rejects_invalid_transition_without_commit():
    repo = FakeRepository()
    service = DispatchService(repo)

    with pytest.raises(ValueError):
        service.update_dispatch_status(repo.dispatch.id, "Completed")

    assert repo.dispatch.dispatch_status == "Assigned"
    assert repo.assignment.status == "Assigned"
    assert repo.emergency.status == "Assigned"
    assert repo.committed is False
    assert repo.logs == []


def test_dispatch_status_detects_state_drift():
    repo = FakeRepository()
    repo.assignment.status = "Accepted"
    service = DispatchService(repo)

    with pytest.raises(ValueError, match="out of sync"):
        service.update_dispatch_status(repo.dispatch.id, "Accepted")

    assert repo.committed is False
    assert repo.logs == []

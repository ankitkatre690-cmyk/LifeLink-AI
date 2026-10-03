import uuid
from types import SimpleNamespace

import pytest

from app.modules.dispatch.service import DispatchService


class FakeRepository:
    def __init__(self):
        self.dispatch = SimpleNamespace(
            id=uuid.uuid4(), emergency_id=uuid.uuid4(), assignment_id=uuid.uuid4(),
            resource_id=uuid.uuid4(), dispatch_status="OnScene"
        )
        self.assignment = SimpleNamespace(status="OnScene")
        self.emergency = SimpleNamespace(status="OnScene")
        self.resource = SimpleNamespace(total_count=5, available_count=3, is_available=True)
        self.logs = []
        self.committed = False

    def get_dispatch(self, dispatch_id):
        return self.dispatch if dispatch_id == self.dispatch.id else None
    def get_assignment(self, assignment_id):
        return self.assignment
    def get_emergency_for_update(self, emergency_id):
        return self.emergency
    def get_hospital_resource(self, resource_id):
        return self.resource
    def create_log(self, log): self.logs.append(log)
    def commit(self): self.committed = True
    def rollback(self): pass
    def refresh(self, entity): return entity


def test_cancellation_releases_hospital_resource_and_closes_workflow():
    repo = FakeRepository()
    service = DispatchService(repo)

    service.update_dispatch_status(repo.dispatch.id, "Cancelled")

    assert repo.dispatch.dispatch_status == "Cancelled"
    assert repo.assignment.status == "Cancelled"
    assert repo.emergency.status == "Cancelled"
    assert repo.resource.available_count == 4
    assert repo.resource.is_available is True
    assert repo.committed is True
    assert len(repo.logs) == 1


def test_cancelled_dispatch_cannot_be_reopened():
    repo = FakeRepository()
    repo.dispatch.dispatch_status = "Cancelled"
    repo.assignment.status = "Cancelled"
    repo.emergency.status = "Cancelled"
    service = DispatchService(repo)

    with pytest.raises(ValueError):
        service.update_dispatch_status(repo.dispatch.id, "Accepted")

    assert repo.committed is False
    assert repo.logs == []

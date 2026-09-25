import threading
import uuid
from types import SimpleNamespace

from app.modules.dispatch.exceptions import DispatchAlreadyExists
from app.modules.dispatch.service import DispatchService


class ConcurrentRepository:
    def __init__(self):
        self.emergency_id = uuid.uuid4()
        self.dispatch = None
        self.lock = threading.Lock()
        self.create_attempts = 0

    def get_emergency_for_update(self, emergency_id):
        if emergency_id != self.emergency_id:
            return None
        return SimpleNamespace(id=self.emergency_id, status="Pending", latitude=20.0, longitude=78.0)

    def get_dispatch_for_emergency(self, emergency_id):
        with self.lock:
            return self.dispatch

    def get_available_responders(self):
        return [SimpleNamespace(id=uuid.uuid4(), latitude=20.1, longitude=78.1, status="Available")]

    def get_available_hospital_resource(self):
        return (
            SimpleNamespace(id=uuid.uuid4(), available_count=1, total_count=1, is_available=True),
            SimpleNamespace(id=uuid.uuid4()),
        )

    def create_assignment(self, assignment):
        with self.lock:
            self.create_attempts += 1
            if self.dispatch is not None:
                raise DispatchAlreadyExists()
        return assignment

    def create_dispatch(self, dispatch):
        with self.lock:
            if self.dispatch is not None:
                raise DispatchAlreadyExists()
            self.dispatch = dispatch
        return dispatch

    def create_log(self, log): pass
    def commit(self): pass
    def rollback(self): pass
    def refresh(self, entity): pass


def test_concurrent_dispatch_allows_only_one_successful_creation():
    repo = ConcurrentRepository()
    results = []
    errors = []

    def run():
        try:
            results.append(DispatchService(repo).dispatch_emergency(repo.emergency_id))
        except DispatchAlreadyExists:
            errors.append("already_exists")

    threads = [threading.Thread(target=run) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(results) == 1
    assert errors == ["already_exists"]
    assert repo.dispatch is not None

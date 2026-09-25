import threading
import uuid
from types import SimpleNamespace

from app.modules.dispatch.exceptions import NoAvailableHospitalResource


class ResourcePool:
    def __init__(self):
        self.resource_id = uuid.uuid4()
        self.available_count = 1
        self.lock = threading.Lock()

    def reserve(self):
        with self.lock:
            if self.available_count <= 0:
                raise NoAvailableHospitalResource()
            self.available_count -= 1
            return SimpleNamespace(id=self.resource_id)


def test_only_one_concurrent_request_can_reserve_final_resource():
    pool = ResourcePool()
    successes = []
    failures = []

    def reserve():
        try:
            successes.append(pool.reserve())
        except NoAvailableHospitalResource:
            failures.append(True)

    threads = [threading.Thread(target=reserve) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(successes) == 1
    assert len(failures) == 1
    assert pool.available_count == 0


def test_resource_cannot_be_reserved_when_count_is_zero():
    pool = ResourcePool()
    pool.available_count = 0

    try:
        pool.reserve()
    except NoAvailableHospitalResource:
        pass
    else:
        raise AssertionError("A zero-count hospital resource must not be reserved.")

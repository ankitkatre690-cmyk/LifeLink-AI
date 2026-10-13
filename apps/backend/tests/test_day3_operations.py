import asyncio
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.modules.hospital.service import HospitalService
from app.modules.police import router as police_router
from app.modules.police.service import PoliceService


class FakeHospitalRepository:
    def __init__(self):
        self.hospital = SimpleNamespace(id=uuid.uuid4(), user_id=uuid.uuid4())
        self.resource = SimpleNamespace(
            id=uuid.uuid4(),
            hospital_id=self.hospital.id,
            total_count=10,
            available_count=4,
            is_available=True,
        )
        self.committed = False

    def get_by_user_id(self, user_id):
        return self.hospital

    def get_resource(self, resource_id):
        return self.resource if resource_id == self.resource.id else None

    def commit(self):
        self.committed = True


def test_hospital_resource_update_derives_availability_from_inventory():
    repo = FakeHospitalRepository()
    service = HospitalService(repo)
    user = SimpleNamespace(
        id=repo.hospital.user_id,
        role=SimpleNamespace(name="Hospital"),
    )
    request = SimpleNamespace(total_count=8, available_count=0)

    resource = service.update_resource(user, repo.resource.id, request)

    assert resource.total_count == 8
    assert resource.available_count == 0
    assert resource.is_available is False
    assert repo.committed is True


class FakePoliceRepository:
    def __init__(self):
        self.case = SimpleNamespace(
            id=uuid.uuid4(),
            emergency_id=uuid.uuid4(),
            police_user_id=uuid.uuid4(),
            case_status="Open",
            notes=None,
            closed_at=None,
        )
        self.emergency = SimpleNamespace(
            id=self.case.emergency_id,
            status="Assigned",
        )
        self.committed = False

    def get_case(self, case_id):
        return self.case if case_id == self.case.id else None

    def user_can_access_case(self, case_id, user_id, role):
        return True

    def get_emergency(self, emergency_id):
        return self.emergency

    def has_active_assignment(self, emergency_id):
        return False

    def commit(self):
        self.committed = True

    def refresh(self, entity):
        return entity


def test_police_case_supports_in_progress_transition():
    repo = FakePoliceRepository()
    service = PoliceService(repo)
    request = SimpleNamespace(case_status="InProgress", notes="Officer assigned to scene.")

    case = service.update_case(
        repo.case.id,
        request,
        repo.case.police_user_id,
        "Police",
    )

    assert case.case_status == "InProgress"
    assert case.closed_at is None
    assert repo.committed is True


def test_police_create_case_publishes_realtime_event():
    police_user_id = uuid.uuid4()
    case_id = uuid.uuid4()
    emergency_id = uuid.uuid4()
    case = SimpleNamespace(
        id=case_id,
        emergency_id=emergency_id,
        case_status="Open",
    )
    fake_service = SimpleNamespace(
        create_case=lambda emergency_id, user_id, request: case,
    )
    user = SimpleNamespace(
        id=police_user_id,
        role=SimpleNamespace(name="Police"),
    )

    with patch.object(
        police_router,
        "PoliceService",
        return_value=fake_service,
    ), patch.object(
        police_router.connection_manager,
        "send_to_user",
        new_callable=AsyncMock,
    ) as send_to_user:
        response = asyncio.run(
            police_router.create_case(
                emergency_id=emergency_id,
                request=SimpleNamespace(notes="Initial report"),
                db=SimpleNamespace(),
                current_user=user,
            )
        )

    assert response is case
    send_to_user.assert_awaited_once()
    target_user, event = send_to_user.await_args.args
    assert target_user == police_user_id
    assert event["event"] == "police.case_created"
    assert event["data"] == {
        "case_id": str(case_id),
        "emergency_id": str(emergency_id),
        "case_status": "Open",
    }
    assert event["timestamp"]

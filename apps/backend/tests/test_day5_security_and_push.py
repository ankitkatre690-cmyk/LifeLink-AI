import uuid
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.modules.admin import router as admin_router
from app.modules.hospital.exceptions import HospitalResourceNotFound
from app.modules.hospital.service import HospitalService
from app.modules.notifications.exceptions import NotificationNotFound
from app.modules.notifications.service import NotificationService
from app.modules.police.service import PoliceService
from app.notifications.push import FirebasePushNotificationProvider, NoOpPushNotificationProvider, PushMessage


def test_admin_dashboard_rejects_non_admin_role():
    citizen = SimpleNamespace(id=uuid.uuid4(), role=SimpleNamespace(name="Citizen"))

    with pytest.raises(HTTPException) as exc_info:
        admin_router.dashboard(db=SimpleNamespace(), current_user=citizen)

    assert exc_info.value.status_code == 403


def test_hospital_cannot_update_another_hospitals_resource():
    hospital_id = uuid.uuid4()
    other_hospital_id = uuid.uuid4()
    user = SimpleNamespace(id=uuid.uuid4(), role=SimpleNamespace(name="Hospital"))
    resource = SimpleNamespace(id=uuid.uuid4(), hospital_id=other_hospital_id)

    class Repository:
        def get_by_user_id(self, user_id):
            return SimpleNamespace(id=hospital_id) if user_id == user.id else None

        def get_resource(self, resource_id):
            return resource if resource_id == resource.id else None

    service = HospitalService(Repository())

    with pytest.raises(HospitalResourceNotFound):
        service.update_resource(
            user,
            resource.id,
            SimpleNamespace(total_count=10, available_count=5),
        )


def test_police_case_access_is_scoped_to_case_owner():
    case_id = uuid.uuid4()
    owner_id = uuid.uuid4()
    case = SimpleNamespace(id=case_id, police_user_id=owner_id)

    class Repository:
        def get_case(self, requested_id):
            return case if requested_id == case_id else None

        def user_can_access_case(self, requested_id, user_id, role):
            return role == "Admin" or (
                role == "Police"
                and requested_id == case_id
                and user_id == owner_id
            )

    service = PoliceService(Repository())

    assert service.get_case_for_user(case_id, owner_id, "Police") is case
    with pytest.raises(PermissionError, match="not authorized"):
        service.get_case_for_user(case_id, uuid.uuid4(), "Police")
    assert service.get_case_for_user(case_id, uuid.uuid4(), "Admin") is case


def test_device_token_unregister_is_scoped_to_authenticated_user():
    token_id = uuid.uuid4()
    owner_id = uuid.uuid4()

    class Repository:
        def get_device_token_for_user(self, requested_token_id, user_id):
            if requested_token_id == token_id and user_id == owner_id:
                return SimpleNamespace(id=token_id, user_id=owner_id)
            return None

        def deactivate_device_token(self, token):
            raise AssertionError("An unowned token must never be deactivated")

    service = NotificationService(Repository())

    with pytest.raises(NotificationNotFound):
        service.unregister_device_token(uuid.uuid4(), token_id)


def test_noop_push_provider_does_not_attempt_external_delivery():
    provider = NoOpPushNotificationProvider()
    message = PushMessage(
        recipient_id=uuid.uuid4(),
        title="Emergency update",
        body="Responder assigned",
        data={"type": "emergency"},
    )

    assert provider.send(message, ["token"]) == []


def test_fcm_provider_requires_credentials_when_enabled():
    provider = FirebasePushNotificationProvider()
    message = PushMessage(
        recipient_id=uuid.uuid4(),
        title="Emergency update",
        body="Responder assigned",
        data={"type": "emergency"},
    )

    with patch("app.notifications.push.settings.FIREBASE_CREDENTIALS_JSON", None):
        with pytest.raises(RuntimeError, match="FIREBASE_CREDENTIALS_JSON"):
            provider.send(message, ["token"])


def test_push_delivery_failure_does_not_block_in_app_notification():
    recipient_id = uuid.uuid4()
    created = []

    class Repository:
        def create(self, notification):
            created.append(notification)
            return notification

        def list_active_device_tokens(self, user_id):
            return [SimpleNamespace(token="registered-token")]

    service = NotificationService(Repository())
    with patch(
        "app.modules.notifications.service.push_provider.send",
        side_effect=RuntimeError("FCM unavailable"),
    ):
        result = service.create_in_app(
            recipient_id=recipient_id,
            title="Emergency update",
            message="Responder assigned",
            notification_type="dispatch.assignment",
        )

    assert result is created[0]
    assert result.recipient_id == recipient_id
    assert result.channel == "InApp"
    assert result.is_read is False

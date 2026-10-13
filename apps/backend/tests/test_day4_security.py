import uuid
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.modules.admin import router as admin_router
from app.modules.notifications.service import NotificationService


def test_admin_cannot_deactivate_own_account():
    user_id = uuid.uuid4()
    user = SimpleNamespace(
        id=user_id,
        role=SimpleNamespace(name="Admin"),
    )
    request = SimpleNamespace(is_active=False)

    with pytest.raises(HTTPException) as exc_info:
        admin_router.update_user_status(
            user_id=user_id,
            request=request,
            db=SimpleNamespace(),
            current_user=user,
        )

    assert exc_info.value.status_code == 400
    assert "own account" in exc_info.value.detail


class FakeNotificationRepository:
    def __init__(self):
        self.notification = SimpleNamespace(
            id=uuid.uuid4(),
            recipient_id=uuid.uuid4(),
            is_read=False,
        )
        self.committed = False

    def get_for_recipient(self, notification_id, recipient_id):
        if (
            notification_id == self.notification.id
            and recipient_id == self.notification.recipient_id
        ):
            return self.notification
        return None

    def commit(self):
        self.committed = True


def test_notification_read_update_is_recipient_scoped():
    repo = FakeNotificationRepository()
    service = NotificationService(repo)

    service.mark_read(
        repo.notification.recipient_id,
        repo.notification.id,
        True,
    )

    assert repo.notification.is_read is True
    assert repo.committed is True


def test_notification_read_update_rejects_other_recipient():
    repo = FakeNotificationRepository()
    service = NotificationService(repo)

    with pytest.raises(Exception):
        service.mark_read(
            uuid.uuid4(),
            repo.notification.id,
            True,
        )

    assert repo.notification.is_read is False
    assert repo.committed is False

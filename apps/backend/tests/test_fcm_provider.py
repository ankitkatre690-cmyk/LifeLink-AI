from uuid import uuid4

from app.notifications.events import notification_to_push
from app.notifications.push import NoOpPushNotificationProvider


def test_notification_to_push_preserves_emergency_context():
    emergency_id = uuid4()
    message = notification_to_push(
        recipient_id=uuid4(),
        title="Emergency assigned",
        message="A responder has been assigned.",
        notification_type="DispatchAssigned",
        emergency_id=emergency_id,
    )

    assert message.title == "Emergency assigned"
    assert message.body == "A responder has been assigned."
    assert message.data == {
        "notification_type": "DispatchAssigned",
        "emergency_id": str(emergency_id),
    }


def test_noop_provider_does_not_fail_without_firebase():
    provider = NoOpPushNotificationProvider()
    message = notification_to_push(
        recipient_id=uuid4(),
        title="Test",
        message="Test message",
        notification_type="Test",
    )

    assert provider.send(message, ["test-token"]) == []

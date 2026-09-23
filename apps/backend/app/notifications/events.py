from uuid import UUID

from app.notifications.push import PushMessage


def notification_to_push(
    recipient_id: UUID,
    title: str,
    message: str,
    notification_type: str,
    emergency_id: UUID | None = None,
) -> PushMessage:
    data = {"notification_type": notification_type}
    if emergency_id is not None:
        data["emergency_id"] = str(emergency_id)

    return PushMessage(
        recipient_id=recipient_id,
        title=title,
        body=message,
        data=data,
    )

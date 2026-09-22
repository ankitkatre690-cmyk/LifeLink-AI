import uuid

from app.database.models.notification import Notification
from app.modules.notifications.exceptions import NotificationNotFound
from app.modules.notifications.repository import NotificationRepository


class NotificationService:
    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    def list_my_notifications(self, user_id: uuid.UUID):
        return self.repository.list_for_recipient(user_id)

    def mark_read(
        self,
        user_id: uuid.UUID,
        notification_id: uuid.UUID,
        is_read: bool,
    ):
        notification = self.repository.get_for_recipient(
            notification_id,
            user_id,
        )
        if notification is None:
            raise NotificationNotFound()

        notification.is_read = is_read
        self.repository.commit()
        return notification

    def create_in_app(
        self,
        recipient_id: uuid.UUID,
        title: str,
        message: str,
        notification_type: str,
        emergency_id: uuid.UUID | None = None,
    ):
        return self.repository.create(
            Notification(
                recipient_id=recipient_id,
                emergency_id=emergency_id,
                notification_type=notification_type,
                title=title,
                message=message,
                channel="InApp",
                is_read=False,
            )
        )

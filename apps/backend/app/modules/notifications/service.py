import logging
import uuid

from app.database.models.notification import Notification
from app.modules.notifications.exceptions import NotificationNotFound
from app.modules.notifications.repository import NotificationRepository
from app.notifications.events import notification_to_push
from app.notifications.push import push_provider

logger = logging.getLogger(__name__)


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
        notification = self.repository.create(
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

        device_tokens = self.repository.list_active_device_tokens(recipient_id)
        token_values = [token.token for token in device_tokens]
        if token_values:
            try:
                invalid_tokens = push_provider.send(
                    notification_to_push(
                        recipient_id=recipient_id,
                        title=title,
                        message=message,
                        notification_type=notification_type,
                        emergency_id=emergency_id,
                    ),
                    token_values,
                )
                self.repository.deactivate_device_tokens(invalid_tokens)
            except Exception:
                # Push delivery must never prevent the persisted in-app emergency
                # notification from completing its normal transaction.
                logger.exception(
                    "Push delivery failed for notification recipient %s",
                    recipient_id,
                )

        return notification

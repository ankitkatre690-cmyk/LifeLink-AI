import uuid

from sqlalchemy.orm import Session

from app.database.models.device_token import DeviceToken
from app.database.models.notification import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, notification: Notification):
        self.db.add(notification)
        self.db.flush()
        return notification

    def list_for_recipient(self, recipient_id: uuid.UUID):
        return (
            self.db.query(Notification)
            .filter(Notification.recipient_id == recipient_id)
            .order_by(Notification.created_at.desc())
            .all()
        )

    def get_for_recipient(
        self,
        notification_id: uuid.UUID,
        recipient_id: uuid.UUID,
    ):
        return (
            self.db.query(Notification)
            .filter(
                Notification.id == notification_id,
                Notification.recipient_id == recipient_id,
            )
            .first()
        )

    def list_active_device_tokens(self, user_id: uuid.UUID) -> list[DeviceToken]:
        return (
            self.db.query(DeviceToken)
            .filter(
                DeviceToken.user_id == user_id,
                DeviceToken.is_active.is_(True),
            )
            .all()
        )

    def deactivate_device_tokens(self, tokens: list[str]) -> None:
        if not tokens:
            return
        (
            self.db.query(DeviceToken)
            .filter(DeviceToken.token.in_(tokens))
            .update(
                {DeviceToken.is_active: False},
                synchronize_session=False,
            )
        )

    def commit(self):
        self.db.commit()

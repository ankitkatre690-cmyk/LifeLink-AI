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


    def get_device_token_for_user(self, token_id: uuid.UUID, user_id: uuid.UUID):
        return (
            self.db.query(DeviceToken)
            .filter(
                DeviceToken.id == token_id,
                DeviceToken.user_id == user_id,
            )
            .first()
        )

    def get_device_token_by_value(self, user_id: uuid.UUID, token: str):
        return (
            self.db.query(DeviceToken)
            .filter(
                DeviceToken.user_id == user_id,
                DeviceToken.token == token,
            )
            .first()
        )

    def create_device_token(self, device_token: DeviceToken):
        self.db.add(device_token)
        self.db.commit()
        self.db.refresh(device_token)
        return device_token

    def save_device_token(self, device_token: DeviceToken):
        self.db.commit()
        self.db.refresh(device_token)
        return device_token

    def deactivate_device_token(self, device_token: DeviceToken):
        device_token.is_active = False
        self.db.commit()

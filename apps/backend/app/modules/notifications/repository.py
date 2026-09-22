import uuid

from sqlalchemy.orm import Session

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

    def commit(self):
        self.db.commit()

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.models.user import User
from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.notifications.exceptions import NotificationNotFound
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.schemas import (
    DeviceTokenCreate,
    DeviceTokenResponse,
    NotificationReadUpdate,
    NotificationResponse,
)
from app.modules.notifications.service import NotificationService


router = APIRouter(prefix="/notifications", tags=["Notifications"])


def _service(db: Session) -> NotificationService:
    return NotificationService(NotificationRepository(db))


@router.get("", response_model=list[NotificationResponse])
def list_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _service(db).list_my_notifications(current_user.id)


@router.patch("/{notification_id}", response_model=NotificationResponse)
def update_notification(
    notification_id: UUID,
    request: NotificationReadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return _service(db).mark_read(
            current_user.id,
            notification_id,
            request.is_read,
        )
    except NotificationNotFound:
        raise HTTPException(404, "Notification not found.")


@router.post("/device-tokens", response_model=DeviceTokenResponse)
def register_device_token(
    request: DeviceTokenCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _service(db).register_device_token(
        current_user.id,
        request.token,
        request.platform,
    )


@router.delete("/device-tokens/{token_id}", status_code=204)
def unregister_device_token(
    token_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        _service(db).unregister_device_token(current_user.id, token_id)
    except NotificationNotFound:
        raise HTTPException(404, "Device token not found.")

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models.device_token import DeviceToken
from app.database.models.user import User
from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.notifications.device_token_schemas import DeviceTokenCreate, DeviceTokenResponse

router = APIRouter(prefix="/notifications/device-tokens", tags=["Notification Device Tokens"])


@router.post("", response_model=DeviceTokenResponse, status_code=status.HTTP_201_CREATED)
def register_device_token(
    request: DeviceTokenCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    token = db.query(DeviceToken).filter(
        DeviceToken.user_id == current_user.id,
        DeviceToken.token == request.token,
    ).first()

    if token:
        token.platform = request.platform
        token.is_active = True
    else:
        token = DeviceToken(
            user_id=current_user.id,
            token=request.token,
            platform=request.platform,
            is_active=True,
        )
        db.add(token)

    db.commit()
    db.refresh(token)
    return DeviceTokenResponse(
        id=str(token.id),
        token=token.token,
        platform=token.platform,
        is_active=token.is_active,
    )


@router.delete("/{token_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_device_token(
    token_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    token = db.query(DeviceToken).filter(
        DeviceToken.id == token_id,
        DeviceToken.user_id == current_user.id,
    ).first()

    if token is None:
        raise HTTPException(404, "Device token not found.")

    token.is_active = False
    db.commit()

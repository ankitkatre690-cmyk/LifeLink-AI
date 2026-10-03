from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.models.user import User
from app.database.session import SessionLocal
from app.realtime.manager import connection_manager

router = APIRouter(tags=["Realtime"])


def _get_authenticated_user_id(token: str | None) -> UUID | None:
    if not token:
        return None

    payload = decode_access_token(token)
    if payload is None:
        return None

    try:
        return UUID(str(payload["sub"]))
    except (KeyError, TypeError, ValueError):
        return None


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    user_id = _get_authenticated_user_id(
        websocket.query_params.get("token")
    )
    if user_id is None:
        await websocket.close(code=1008, reason="Invalid token")
        return

    db: Session = SessionLocal()
    try:
        user = (
            db.query(User)
            .filter(
                User.id == user_id,
                User.is_active.is_(True),
            )
            .first()
        )
    finally:
        db.close()

    if user is None:
        await websocket.close(code=1008, reason="User not found")
        return

    await connection_manager.connect(user.id, websocket)

    try:
        await websocket.send_json({
            "event": "connected",
            "data": {"user_id": str(user.id)},
        })

        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await connection_manager.disconnect(user.id, websocket)

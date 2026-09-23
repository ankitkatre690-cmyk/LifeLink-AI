from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import SessionLocal
from app.database.models.user import User
from app.realtime.manager import connection_manager

router = APIRouter(tags=["Realtime"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Missing token")
        return

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        subject = payload.get("sub")
        if not subject:
            raise JWTError()
        user_id = subject
    except JWTError:
        await websocket.close(code=1008, reason="Invalid token")
        return

    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
        if user is None:
            await websocket.close(code=1008, reason="User not found")
            return

        await connection_manager.connect(user.id, websocket)
        await websocket.send_json({
            "event": "connected",
            "data": {"user_id": str(user.id)},
        })

        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await connection_manager.disconnect(user.id if "user" in locals() and user else user_id, websocket)
        db.close()

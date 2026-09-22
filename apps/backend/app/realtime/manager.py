import asyncio
from collections import defaultdict
from uuid import UUID

from fastapi import WebSocket


class ConnectionManager:
    """In-memory WebSocket connection manager for a single API instance."""

    def __init__(self):
        self._connections: dict[UUID, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, user_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[user_id].add(websocket)

    async def disconnect(self, user_id: UUID, websocket: WebSocket) -> None:
        async with self._lock:
            connections = self._connections.get(user_id)
            if not connections:
                return
            connections.discard(websocket)
            if not connections:
                self._connections.pop(user_id, None)

    async def send_to_user(self, user_id: UUID, message: dict) -> None:
        async with self._lock:
            connections = list(self._connections.get(user_id, set()))

        stale = []
        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception:
                stale.append(websocket)

        for websocket in stale:
            await self.disconnect(user_id, websocket)

    async def broadcast(self, message: dict) -> None:
        async with self._lock:
            targets = [
                (user_id, websocket)
                for user_id, sockets in self._connections.items()
                for websocket in sockets
            ]

        stale = []
        for _, websocket in targets:
            try:
                await websocket.send_json(message)
            except Exception:
                stale.append(websocket)

        for user_id, websocket in targets:
            if websocket in stale:
                await self.disconnect(user_id, websocket)


connection_manager = ConnectionManager()

from datetime import datetime, timezone
from typing import Any


def build_event(event_type: str, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "event": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }


def build_emergency_status_event(emergency_id: Any, status: str) -> dict[str, Any]:
    return build_event(
        "emergency.status_changed",
        {
            "emergency_id": str(emergency_id),
            "status": status,
        },
    )

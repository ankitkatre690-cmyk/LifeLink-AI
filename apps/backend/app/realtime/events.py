from datetime import datetime, timezone
from typing import Any


def build_event(event_type: str, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "event": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }

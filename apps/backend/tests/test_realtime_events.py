from app.realtime.events import build_emergency_status_event


def test_build_emergency_status_event_is_authoritative():
    event = build_emergency_status_event(
        "4e6d7f20-5a0a-4b1d-8c65-9f4b1d2c7e31",
        "Assigned",
    )

    assert event["event"] == "emergency.status_changed"
    assert event["data"] == {
        "emergency_id": "4e6d7f20-5a0a-4b1d-8c65-9f4b1d2c7e31",
        "status": "Assigned",
    }
    assert event["timestamp"]

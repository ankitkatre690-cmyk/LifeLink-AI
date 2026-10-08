import asyncio
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.modules.police import router as police_router


def test_police_update_case_publishes_realtime_event():
    police_user_id = uuid.uuid4()
    case_id = uuid.uuid4()
    emergency_id = uuid.uuid4()
    case = SimpleNamespace(
        id=case_id,
        emergency_id=emergency_id,
        case_status="InProgress",
    )
    fake_service = SimpleNamespace(
        update_case=lambda case_id, request, user_id, role: case,
    )
    user = SimpleNamespace(
        id=police_user_id,
        role=SimpleNamespace(name="Police"),
    )

    with patch.object(
        police_router,
        "PoliceService",
        return_value=fake_service,
    ), patch.object(
        police_router.connection_manager,
        "send_to_user",
        new_callable=AsyncMock,
    ) as send_to_user:
        response = asyncio.run(
            police_router.update_case(
                case_id=case_id,
                request=SimpleNamespace(
                    case_status="InProgress",
                    notes="Officer dispatched.",
                ),
                db=SimpleNamespace(),
                current_user=user,
            )
        )

    assert response is case
    send_to_user.assert_awaited_once()
    target_user, event = send_to_user.await_args.args
    assert target_user == police_user_id
    assert event["event"] == "police.case_status_changed"
    assert event["data"] == {
        "case_id": str(case_id),
        "emergency_id": str(emergency_id),
        "case_status": "InProgress",
    }
    assert event["timestamp"]

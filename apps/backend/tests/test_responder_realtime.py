import asyncio
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.modules.responder import router


def test_responder_location_route_publishes_realtime_event():
    user_id = uuid.uuid4()
    responder_id = uuid.uuid4()
    emergency_id = uuid.uuid4()
    assignment_id = uuid.uuid4()
    citizen_id = uuid.uuid4()

    profile = SimpleNamespace(
        id=responder_id,
        user_id=user_id,
        latitude=21.1500,
        longitude=79.0900,
    )
    assignment = SimpleNamespace(
        id=assignment_id,
        emergency_id=emergency_id,
        status="EnRoute",
        emergency=SimpleNamespace(citizen_id=citizen_id),
    )
    fake_service = SimpleNamespace(
        update_location=lambda user, latitude, longitude: profile,
    )
    fake_repository = SimpleNamespace(
        get_active_assignments_for_responder=lambda profile_id: [assignment],
    )
    fake_family_repository = SimpleNamespace(
        get_member_user_ids_for_creator=lambda creator_id: [],
    )
    user = SimpleNamespace(
        id=user_id,
        role=SimpleNamespace(name="Responder"),
    )

    with patch.object(router, "_service", return_value=fake_service),          patch.object(router, "ResponderRepository", return_value=fake_repository),          patch.object(router, "FamilyRepository", return_value=fake_family_repository),          patch.object(
             router.connection_manager,
             "send_to_user",
             new_callable=AsyncMock,
         ) as send_to_user:
        response = asyncio.run(
            router.update_my_location(
                request=SimpleNamespace(latitude=21.1500, longitude=79.0900),
                db=SimpleNamespace(),
                current_user=user,
            )
        )

    assert response is profile
    send_to_user.assert_awaited_once_with(
        citizen_id,
        {
            "event": "responder.location_updated",
            "data": {
                "assignment_id": str(assignment_id),
                "emergency_id": str(emergency_id),
                "responder_id": str(responder_id),
                "latitude": 21.15,
                "longitude": 79.09,
                "assignment_status": "EnRoute",
            },
            "timestamp": send_to_user.await_args.args[1]["timestamp"],
        },
    )


def test_responder_assignment_status_event_is_not_duplicated():
    user_id = uuid.uuid4()
    responder_id = uuid.uuid4()
    emergency_id = uuid.uuid4()
    assignment_id = uuid.uuid4()
    citizen_id = uuid.uuid4()

    assignment = SimpleNamespace(
        id=assignment_id,
        emergency_id=emergency_id,
        responder_id=responder_id,
        status="Accepted",
        notes="Accepted assignment.",
        emergency=SimpleNamespace(
            citizen_id=citizen_id,
            status="Accepted",
        ),
        responder=SimpleNamespace(user_id=user_id),
    )
    fake_service = SimpleNamespace(
        update_assignment=lambda user, assignment_id, status, notes: assignment,
    )
    fake_family_repository = SimpleNamespace(
        get_member_user_ids_for_creator=lambda creator_id: [],
    )
    user = SimpleNamespace(
        id=user_id,
        role=SimpleNamespace(name="Responder"),
    )

    with patch.object(
        router,
        "_service",
        return_value=fake_service,
    ), patch.object(
        router,
        "FamilyRepository",
        return_value=fake_family_repository,
    ), patch.object(
        router.connection_manager,
        "send_to_user",
        new_callable=AsyncMock,
    ) as send_to_user:
        response = asyncio.run(
            router.update_assignment(
                assignment_id=assignment_id,
                request=SimpleNamespace(
                    status="Accepted",
                    notes="Accepted assignment.",
                ),
                db=SimpleNamespace(),
                current_user=user,
            )
        )

    assert response is assignment
    send_to_user.assert_awaited_once()
    target_user, event = send_to_user.await_args.args
    assert target_user == citizen_id
    assert event["event"] == "responder.assignment_status_changed"
    assert event["data"]["assignment_id"] == str(assignment_id)
    assert event["data"]["status"] == "Accepted"

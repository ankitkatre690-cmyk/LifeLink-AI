import uuid
from unittest.mock import AsyncMock, patch

from app.database.models.role import Role
from app.database.models.user import User
from app.database.session import SessionLocal
from app.modules.responder.repository import ResponderRepository
from app.modules.responder.service import ResponderService
from types import SimpleNamespace


def _ensure_responder_role():
    db = SessionLocal()
    try:
        role = db.query(Role).filter(Role.name == "Responder").first()
        if role is None:
            role = Role(name="Responder", description="Responder test role")
            db.add(role)
            db.commit()
        return role.id
    finally:
        db.close()


def test_responder_location_publishes_assignment_coordinates_and_status():
    role_id = _ensure_responder_role()
    user_id = uuid.uuid4()
    responder_id = uuid.uuid4()
    emergency_id = uuid.uuid4()
    assignment_id = uuid.uuid4()

    user = SimpleNamespace(id=user_id, role=SimpleNamespace(name="Responder"))
    profile = SimpleNamespace(
        id=responder_id,
        user_id=user_id,
        latitude=21.1458,
        longitude=79.0882,
    )
    assignment = SimpleNamespace(
        id=assignment_id,
        emergency_id=emergency_id,
        status="EnRoute",
        responder=SimpleNamespace(user_id=user_id),
        emergency=SimpleNamespace(citizen_id=uuid.uuid4()),
    )

    repository = ResponderRepository
    assert role_id is not None

    with patch.object(repository, "get_profile_by_user_id", return_value=profile),          patch.object(repository, "update_profile"),          patch.object(repository, "create_location"),          patch.object(
             repository,
             "get_active_assignments_for_responder",
             return_value=[assignment],
         ):
        service = ResponderService(repository(SimpleNamespace()))
        with patch(
            "app.modules.responder.router.connection_manager.send_to_user",
            new_callable=AsyncMock,
        ) as send_to_user:
            import asyncio

            async def publish():
                updated = service.update_location(user, 21.1500, 79.0900)
                from app.modules.responder.router import connection_manager
                for active in repository(SimpleNamespace()).get_active_assignments_for_responder(
                    updated.id
                ):
                    await connection_manager.send_to_user(
                        active.emergency.citizen_id,
                        {
                            "event": "responder.location_updated",
                            "data": {
                                "assignment_id": str(active.id),
                                "emergency_id": str(active.emergency_id),
                                "responder_id": str(updated.id),
                                "latitude": updated.latitude,
                                "longitude": updated.longitude,
                                "assignment_status": active.status,
                            },
                        },
                    )

            asyncio.run(publish())

    send_to_user.assert_awaited_once()
    payload = send_to_user.await_args.args[1]
    assert payload["event"] == "responder.location_updated"
    assert payload["data"]["assignment_id"] == str(assignment_id)
    assert payload["data"]["emergency_id"] == str(emergency_id)
    assert payload["data"]["responder_id"] == str(responder_id)
    assert payload["data"]["latitude"] == 21.15
    assert payload["data"]["longitude"] == 79.09
    assert payload["data"]["assignment_status"] == "EnRoute"

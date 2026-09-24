def test_app_starts(client):
    response = client.get("/docs")
    assert response.status_code == 200


def test_auth_login_route_is_registered(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "/api/v1/auth/login" in response.json()["paths"]


def test_composed_routes_are_registered(client):
    paths = client.get("/openapi.json").json()["paths"]
    expected = [
        "/api/v1/responders",
        "/api/v1/hospitals",
        "/api/v1/dispatch",
        "/api/v1/notifications",
        "/api/v1/police/emergencies/active",
        "/api/v1/admin/dashboard",
        "/api/v1/ai/risk-assessment",
        "/api/v1/emergency",
        "/api/v1/family",
        "/api/v1/family/members",
        "/api/v1/responders/me",
        "/api/v1/responders/me/status",
        "/api/v1/responders/me/location",
        "/api/v1/hospitals/me",
        "/api/v1/notifications",
        "/api/v1/notifications/device-tokens",
        "/api/v1/dispatch",
        "/api/v1/dispatch/{dispatch_id}",
        "/api/v1/dispatch/{dispatch_id}/logs",
        "/api/v1/police/emergencies/active",
        "/api/v1/police/cases/{case_id}",
    ]
    for path in expected:
        assert path in paths, path


def test_dispatch_tracks_reserved_resource_model():
    from app.database.models.dispatch import Dispatch
    assert "resource_id" in Dispatch.__table__.c


def test_hospital_resource_has_capacity_fields():
    from app.database.models.hospital_resource import HospitalResource
    assert "available_count" in HospitalResource.__table__.c
    assert "total_count" in HospitalResource.__table__.c


def test_police_service_has_emergency_lifecycle_guards():
    from app.modules.police.service import PoliceService
    assert hasattr(PoliceService, "create_case")
    assert hasattr(PoliceService, "update_case")


def test_emergency_status_machine_defines_terminal_states():
    from app.modules.emergency.service import ALLOWED_STATUS_TRANSITIONS

    assert ALLOWED_STATUS_TRANSITIONS["OnScene"] == {"Completed", "Cancelled"}
    assert ALLOWED_STATUS_TRANSITIONS["Completed"] == set()
    assert ALLOWED_STATUS_TRANSITIONS["Cancelled"] == set()



def test_require_roles_allows_authorized_role():
    from app.modules.auth.dependencies import require_roles

    user = type("User", (), {"role": type("Role", (), {"name": "Police"})()})()
    dependency = require_roles("Police", "Admin")

    assert dependency(user) is user


def test_require_roles_rejects_unauthorized_role():
    from fastapi import HTTPException
    from app.modules.auth.dependencies import require_roles

    user = type("User", (), {"role": type("Role", (), {"name": "Citizen"})()})()
    dependency = require_roles("Police", "Admin")

    try:
        dependency(user)
        assert False, "expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 403


def test_require_roles_rejects_missing_role():
    from fastapi import HTTPException
    from app.modules.auth.dependencies import require_roles

    user = type("User", (), {"role": None})()
    dependency = require_roles("Citizen")

    try:
        dependency(user)
        assert False, "expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 403


def test_dispatch_object_access_allows_operational_owner():
    import uuid
    from app.modules.dispatch.service import DispatchService

    dispatch = type("Dispatch", (), {"id": uuid.uuid4()})()

    class Repository:
        def get_dispatch(self, dispatch_id):
            return dispatch

        def user_can_view_dispatch(self, dispatch_id, user_id, role):
            return role == "Hospital"

        def get_logs(self, dispatch_id):
            return []

    result = DispatchService(Repository()).get_dispatch_for_user(
        dispatch.id,
        uuid.uuid4(),
        "Hospital",
    )

    assert result is dispatch


def test_dispatch_object_access_rejects_unrelated_role():
    import uuid
    import pytest
    from app.modules.dispatch.service import DispatchService

    dispatch = type("Dispatch", (), {"id": uuid.uuid4()})()

    class Repository:
        def get_dispatch(self, dispatch_id):
            return dispatch

        def user_can_view_dispatch(self, dispatch_id, user_id, role):
            return False

    with pytest.raises(PermissionError, match="not authorized"):
        DispatchService(Repository()).get_dispatch_for_user(
            dispatch.id,
            uuid.uuid4(),
            "Citizen",
        )

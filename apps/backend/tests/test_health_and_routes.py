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

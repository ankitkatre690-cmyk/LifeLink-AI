import uuid
from urllib.parse import urlencode

from app.database.models.role import Role
from app.database.models.user import User
from app.database.session import SessionLocal


ROLES = ("Citizen", "Police", "Responder", "Hospital")


def _ensure_roles() -> None:
    db = SessionLocal()
    try:
        existing = {role.name for role in db.query(Role).all()}
        for name in ROLES:
            if name not in existing:
                db.add(Role(name=name, description=f"{name} test role"))
        db.commit()
    finally:
        db.close()


def _register_and_login(client, role: str):
    email = f"e2e-{role.lower()}-{uuid.uuid4()}@example.com"
    password = "E2ETest123!"
    phone = f"8{uuid.uuid4().int % 10**9:09d}"

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "phone": phone,
            "password": password,
            "role": role,
        },
    )
    assert response.status_code == 201, response.text
    user_id = response.json()["id"]

    response = client.post(
        "/api/v1/auth/login",
        data=urlencode({"username": email, "password": password}),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200, response.text
    return user_id, {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_end_to_end_emergency_dispatch_responder_hospital_flow(client):
    """
    Verify the real HTTP workflow across the operational roles:

    Citizen creates emergency -> Police dispatches -> nearest available
    Responder is assigned -> Hospital resource is reserved -> Responder
    progresses through the assignment -> resource is released on completion.
    """
    _ensure_roles()
    created_user_ids = []

    try:
        citizen_id, citizen_headers = _register_and_login(client, "Citizen")
        police_id, police_headers = _register_and_login(client, "Police")
        responder_id, responder_headers = _register_and_login(client, "Responder")
        hospital_user_id, hospital_headers = _register_and_login(client, "Hospital")
        created_user_ids.extend(
            [citizen_id, police_id, responder_id, hospital_user_id]
        )

        responder_response = client.post(
            "/api/v1/responders",
            json={
                "responder_type": "Ambulance",
                "vehicle_number": "E2E-AMB-01",
                "latitude": 21.1450,
                "longitude": 79.0875,
            },
            headers=responder_headers,
        )
        assert responder_response.status_code == 201, responder_response.text
        responder_profile_id = responder_response.json()["id"]

        hospital_response = client.post(
            "/api/v1/hospitals",
            json={
                "name": "E2E General Hospital",
                "address": "Nagpur, Maharashtra",
                "phone": "07121234567",
            },
            headers=hospital_headers,
        )
        assert hospital_response.status_code == 201, hospital_response.text
        hospital_id = hospital_response.json()["id"]

        resource_response = client.post(
            "/api/v1/hospitals/resources",
            json={
                "resource_type": "ICU",
                "total_count": 1,
                "available_count": 1,
            },
            headers=hospital_headers,
        )
        assert resource_response.status_code == 201, resource_response.text
        resource_id = resource_response.json()["id"]

        emergency_response = client.post(
            "/api/v1/emergency",
            json={
                "emergency_type": "Medical",
                "latitude": 21.1458,
                "longitude": 79.0882,
                "description": "End-to-end emergency response test",
            },
            headers=citizen_headers,
        )
        assert emergency_response.status_code == 201, emergency_response.text
        emergency = emergency_response.json()
        emergency_id = emergency["id"]
        assert emergency["status"] == "Pending"

        # Operational endpoints must enforce role boundaries at the HTTP layer,
        # not merely inside service-level unit tests.
        forbidden_dispatch = client.post(
            "/api/v1/dispatch",
            json={"emergency_id": emergency_id},
            headers=citizen_headers,
        )
        assert forbidden_dispatch.status_code == 403, forbidden_dispatch.text

        forbidden_admin_dashboard = client.get(
            "/api/v1/admin/dashboard",
            headers=citizen_headers,
        )
        assert forbidden_admin_dashboard.status_code == 403, forbidden_admin_dashboard.text

        forbidden_responder_dispatch = client.post(
            "/api/v1/dispatch",
            json={"emergency_id": emergency_id},
            headers=responder_headers,
        )
        assert forbidden_responder_dispatch.status_code == 403, forbidden_responder_dispatch.text

        dispatch_response = client.post(
            "/api/v1/dispatch",
            json={"emergency_id": emergency_id},
            headers=police_headers,
        )
        assert dispatch_response.status_code == 201, dispatch_response.text
        dispatch = dispatch_response.json()
        dispatch_id = dispatch["id"]
        assignment_id = dispatch["assignment_id"]
        assert dispatch["dispatch_status"] == "Assigned"
        assert dispatch["hospital_id"] == hospital_id

        resources = client.get(
            f"/api/v1/hospitals/{hospital_id}/resources",
            headers=hospital_headers,
        )
        assert resources.status_code == 200, resources.text
        resource = next(item for item in resources.json() if item["id"] == resource_id)
        assert resource["available_count"] == 0
        assert resource["is_available"] is False

        active_assignment = client.get(
            "/api/v1/responders/assignments/active",
            headers=responder_headers,
        )
        assert active_assignment.status_code == 200, active_assignment.text
        assert active_assignment.json()["id"] == assignment_id
        assert active_assignment.json()["responder_id"] == responder_profile_id
        assert active_assignment.json()["status"] == "Assigned"

        for status, expected_emergency_status in (
            ("Accepted", "Accepted"),
            ("EnRoute", "EnRoute"),
            ("OnScene", "OnScene"),
            ("Completed", "Completed"),
        ):
            response = client.patch(
                f"/api/v1/responders/assignments/{assignment_id}",
                json={"status": status},
                headers=responder_headers,
            )
            assert response.status_code == 200, response.text
            assert response.json()["status"] == status

            emergency_response = client.get(
                f"/api/v1/emergency/{emergency_id}",
                headers=citizen_headers,
            )
            assert emergency_response.status_code == 200, emergency_response.text
            assert emergency_response.json()["status"] == expected_emergency_status

        dispatch_response = client.get(
            f"/api/v1/dispatch/{dispatch_id}",
            headers=police_headers,
        )
        assert dispatch_response.status_code == 200, dispatch_response.text
        assert dispatch_response.json()["dispatch_status"] == "Completed"

        resources = client.get(
            f"/api/v1/hospitals/{hospital_id}/resources",
            headers=hospital_headers,
        )
        assert resources.status_code == 200, resources.text
        resource = next(item for item in resources.json() if item["id"] == resource_id)
        assert resource["available_count"] == 1
        assert resource["is_available"] is True

        responder_response = client.get(
            "/api/v1/responders/me",
            headers=responder_headers,
        )
        assert responder_response.status_code == 200, responder_response.text
        assert responder_response.json()["status"] == "Available"
    finally:
        db = SessionLocal()
        try:
            for user_id in created_user_ids:
                user = db.get(User, user_id)
                if user is not None:
                    db.delete(user)
            db.commit()
        finally:
            db.close()

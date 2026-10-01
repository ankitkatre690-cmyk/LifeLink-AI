import uuid
from urllib.parse import urlencode

from app.database.models.role import Role
from app.database.models.user import User
from app.database.session import SessionLocal


def _ensure_citizen_role() -> None:
    db = SessionLocal()
    try:
        role = db.query(Role).filter(Role.name == "Citizen").first()
        if role is None:
            db.add(Role(name="Citizen", description="Citizen user"))
            db.commit()
    finally:
        db.close()


def test_citizen_api_smoke_flow(client):
    """
    Sequential API smoke test for the core citizen emergency journey.

    The test uses the real HTTP routes through FastAPI TestClient and prepares
    only the required Citizen role directly in the test database.
    """
    _ensure_citizen_role()

    email = f"smoke-{uuid.uuid4()}@example.com"
    password = "SmokeTest123!"
    phone = f"9{uuid.uuid4().int % 10**9:09d}"
    user_id = None

    steps = [
        "register",
        "login",
        "me",
        "create_profile",
        "get_profile",
        "create_emergency",
        "get_emergency",
        "cancel_emergency",
        "timeline",
        "register_device_token",
        "delete_device_token",
    ]

    def step(name: str, response, expected: int) -> None:
        print(f"[{steps.index(name) + 1}/{len(steps)}] {name}: {response.status_code}")
        assert response.status_code == expected, response.text

    try:
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "phone": phone,
                "password": password,
                "role": "Citizen",
            },
        )
        step("register", response, 201)
        user_id = response.json()["id"]
        assert response.json()["role"] == "Citizen"
        assert response.json()["is_active"] is True
        assert response.json()["is_verified"] is False

        response = client.post(
            "/api/v1/auth/login",
            data=urlencode({"username": email, "password": password}),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        step("login", response, 200)
        token = response.json()["access_token"]
        assert response.json()["token_type"] == "bearer"

        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/auth/me", headers=headers)
        step("me", response, 200)
        assert response.json()["id"] == user_id
        assert response.json()["role"] == "Citizen"

        profile = {
            "first_name": "Smoke",
            "last_name": "Tester",
            "gender": "Other",
            "date_of_birth": "2000-01-01",
            "blood_group": "O+",
            "address": "Test Address",
            "city": "Nagpur",
            "state": "Maharashtra",
            "country": "India",
            "pincode": "440001",
            "emergency_contact_name": "Emergency Contact",
            "emergency_contact_phone": "9876543210",
            "allergies": None,
            "medical_conditions": None,
            "medications": None,
            "organ_donor": False,
            "height": 170,
            "weight": 65,
        }

        response = client.post(
            "/api/v1/citizen/profile",
            json=profile,
            headers=headers,
        )
        step("create_profile", response, 201)
        assert response.json()["user_id"] == user_id

        response = client.get("/api/v1/citizen/profile", headers=headers)
        step("get_profile", response, 200)
        assert response.json()["first_name"] == "Smoke"

        response = client.post(
            "/api/v1/emergency",
            json={
                "emergency_type": "Medical",
                "latitude": 21.1458,
                "longitude": 79.0882,
                "description": "Automated smoke test emergency",
            },
            headers=headers,
        )
        step("create_emergency", response, 201)
        emergency_id = response.json()["id"]
        assert response.json()["citizen_id"] == user_id
        assert response.json()["status"] == "Pending"

        response = client.get(
            f"/api/v1/emergency/{emergency_id}",
            headers=headers,
        )
        step("get_emergency", response, 200)
        assert response.json()["id"] == emergency_id

        response = client.patch(
            f"/api/v1/emergency/{emergency_id}",
            json={
                "status": "Cancelled",
                "remarks": "Automated smoke test cleanup",
            },
            headers=headers,
        )
        step("cancel_emergency", response, 200)
        assert response.json()["status"] == "Cancelled"

        response = client.get(
            f"/api/v1/emergency/{emergency_id}/timeline",
            headers=headers,
        )
        step("timeline", response, 200)
        assert isinstance(response.json(), list)
        assert any(item["status"] == "Cancelled" for item in response.json())

        device_token = f"smoke-token-{uuid.uuid4()}"
        response = client.post(
            "/api/v1/notifications/device-tokens",
            json={"token": device_token, "platform": "android"},
            headers=headers,
        )
        step("register_device_token", response, 200)
        token_id = response.json()["id"]
        assert response.json()["user_id"] == user_id
        assert response.json()["token"] == device_token
        assert response.json()["is_active"] is True

        response = client.delete(
            f"/api/v1/notifications/device-tokens/{token_id}",
            headers=headers,
        )
        step("delete_device_token", response, 204)
    finally:
        if user_id is not None:
            db = SessionLocal()
            try:
                user = db.get(User, user_id)
                if user is not None:
                    db.delete(user)
                    db.commit()
            finally:
                db.close()

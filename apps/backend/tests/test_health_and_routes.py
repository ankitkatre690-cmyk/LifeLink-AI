def test_app_starts(client):
    response = client.get("/docs")
    assert response.status_code == 200


def test_auth_login_route_exists(client):
    response = client.post("/api/v1/auth/login", data={
        "username": "missing@example.com",
        "password": "invalid",
    })
    assert response.status_code in {401, 422}

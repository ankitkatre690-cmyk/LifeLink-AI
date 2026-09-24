def test_app_starts(client):
    response = client.get("/docs")
    assert response.status_code == 200


def test_auth_login_route_is_registered(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "/api/v1/auth/login" in response.json()["paths"]

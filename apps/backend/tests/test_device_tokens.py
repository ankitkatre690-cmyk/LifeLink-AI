def test_device_token_requires_authentication(client):
    response = client.post(
        "/api/v1/notifications/device-tokens",
        json={"token": "test-token", "platform": "android"},
    )
    assert response.status_code == 401


def test_device_token_delete_requires_authentication(client):
    response = client.delete(
        "/api/v1/notifications/device-tokens/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 401

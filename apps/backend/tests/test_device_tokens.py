def test_device_token_endpoint_is_registered(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert "/api/v1/notifications/device-tokens" in paths

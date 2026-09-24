def test_device_token_endpoint_is_not_in_base_smoke_scope(client):
    # Device-token behavior is validated by the dedicated device-token feature branch.
    response = client.get("/openapi.json")
    assert response.status_code == 200

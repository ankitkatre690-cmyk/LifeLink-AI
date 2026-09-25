import logging


def test_audit_request_adds_request_id_and_logs(client, caplog):
    with caplog.at_level(logging.INFO, logger="lifelink.audit"):
        response = client.get("/docs", params={"token": "do-not-log"})

    assert response.status_code == 200
    request_id = response.headers.get("X-Request-ID")
    assert request_id
    assert "do-not-log" not in caplog.text
    assert "request.completed" in caplog.text
    assert request_id in caplog.text


def test_audit_request_preserves_client_request_id(client, caplog):
    with caplog.at_level(logging.INFO, logger="lifelink.audit"):
        response = client.get(
            "/docs",
            headers={"X-Request-ID": "client-request-123"},
        )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "client-request-123"
    assert "client-request-123" in caplog.text

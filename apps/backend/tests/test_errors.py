from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.errors import register_error_handlers


def _app():
    app = FastAPI()
    register_error_handlers(app)

    @app.get("/validation")
    def validation(value: int):
        return {"value": value}

    @app.get("/boom")
    def boom():
        raise RuntimeError("secret internal detail")

    return app


def test_validation_error_has_stable_shape_and_request_id():
    client = TestClient(_app())
    response = client.get("/validation?value=not-an-int")

    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "VALIDATION_ERROR"
    assert body["request_id"]
    assert response.headers["X-Request-ID"] == body["request_id"]


def test_unhandled_error_does_not_expose_internal_detail():
    client = TestClient(_app(), raise_server_exceptions=False)
    response = client.get("/boom")

    assert response.status_code == 500
    body = response.json()
    assert body["error"] == "INTERNAL_SERVER_ERROR"
    assert "secret internal detail" not in response.text
    assert response.headers["X-Request-ID"] == body["request_id"]

from datetime import timedelta

from app.core.security import create_access_token, decode_access_token
from app.realtime.router import _get_authenticated_user_id


def test_access_token_contains_explicit_access_type():
    token = create_access_token("00000000-0000-0000-0000-000000000001")

    payload = decode_access_token(token)

    assert payload is not None
    assert payload["typ"] == "access"


def test_websocket_auth_rejects_missing_token():
    assert _get_authenticated_user_id(None) is None


def test_websocket_auth_rejects_invalid_uuid_subject():
    token = create_access_token("not-a-uuid")

    assert _get_authenticated_user_id(token) is None


def test_websocket_auth_rejects_expired_token():
    token = create_access_token(
        "00000000-0000-0000-0000-000000000001",
        expires_delta=timedelta(seconds=-1),
    )

    assert _get_authenticated_user_id(token) is None

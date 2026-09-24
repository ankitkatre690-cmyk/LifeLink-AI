import uuid

import pytest
from fastapi import HTTPException

from app.modules.auth import dependencies


class FakeQuery:
    def __init__(self, user):
        self.user = user

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return self.user


class FakeDB:
    def __init__(self, user):
        self.user = user

    def query(self, *_args, **_kwargs):
        return FakeQuery(self.user)


def test_get_current_user_rejects_missing_subject(monkeypatch):
    monkeypatch.setattr(dependencies, "decode_access_token", lambda _token: {})

    with pytest.raises(HTTPException) as exc:
        dependencies.get_current_user(FakeDB(None), "token")

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token subject"


def test_get_current_user_rejects_malformed_subject(monkeypatch):
    monkeypatch.setattr(
        dependencies,
        "decode_access_token",
        lambda _token: {"sub": "not-a-uuid"},
    )

    with pytest.raises(HTTPException) as exc:
        dependencies.get_current_user(FakeDB(None), "token")

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token subject"


def test_get_current_user_rejects_missing_user(monkeypatch):
    monkeypatch.setattr(
        dependencies,
        "decode_access_token",
        lambda _token: {"sub": str(uuid.uuid4())},
    )

    with pytest.raises(HTTPException) as exc:
        dependencies.get_current_user(FakeDB(None), "token")

    assert exc.value.status_code == 401
    assert exc.value.detail == "User not found"


def test_get_current_user_rejects_inactive_user(monkeypatch):
    inactive_user = type("UserStub", (), {"is_active": False})()
    monkeypatch.setattr(
        dependencies,
        "decode_access_token",
        lambda _token: {"sub": str(uuid.uuid4())},
    )

    with pytest.raises(HTTPException) as exc:
        dependencies.get_current_user(FakeDB(inactive_user), "token")

    assert exc.value.status_code == 401
    assert exc.value.detail == "User account is inactive"


def test_get_current_user_returns_active_user(monkeypatch):
    active_user = type("UserStub", (), {"is_active": True})()
    monkeypatch.setattr(
        dependencies,
        "decode_access_token",
        lambda _token: {"sub": str(uuid.uuid4())},
    )

    result = dependencies.get_current_user(FakeDB(active_user), "token")

    assert result is active_user

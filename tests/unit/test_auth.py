from __future__ import annotations

from datetime import UTC

import pytest
from fastapi import HTTPException

from cronos.auth import create_token, decode_token, hash_password, verify_password


def test_hash_and_verify():
    hashed = hash_password("testpass")
    assert verify_password("testpass", hashed) is True
    assert verify_password("wrongpass", hashed) is False


def test_create_and_decode_token(monkeypatch):
    monkeypatch.setattr("cronos.auth.settings.cronos_auth_secret", "a" * 32)
    token = create_token("testuser", "admin")
    payload = decode_token(token)
    assert payload.sub == "testuser"
    assert payload.role == "admin"


def test_token_expired(monkeypatch):
    monkeypatch.setattr("cronos.auth.settings.cronos_auth_secret", "a" * 32)
    from datetime import datetime, timedelta

    import jwt
    token = jwt.encode(
        {"sub": "u", "role": "op", "exp": datetime.now(UTC) - timedelta(hours=1)},
        "a" * 32,
        algorithm="HS256",
    )
    with pytest.raises(HTTPException) as exc:
        decode_token(token)
    assert exc.value.status_code == 401


def test_weak_secret():
    import pytest

    from cronos.auth import create_token as ct
    with pytest.raises(ValueError, match="at least 32 characters"):
        ct("user", "op")

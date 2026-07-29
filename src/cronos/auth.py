from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy import select

from cronos.config import settings

# ruff: noqa: B008
from cronos.persistence.db import get_engine
from cronos.persistence.schema import users_table

ph = PasswordHasher()
security = HTTPBearer(auto_error=False)

_failed_attempts: dict[str, list[datetime]] = {}
LOCKOUT_THRESHOLD = 5
LOCKOUT_WINDOW_MINUTES = 15
RATE_LIMIT_PER_MINUTE = 5


class TokenPayload(BaseModel):
    sub: str
    role: str
    exp: int


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, password)
    except (VerificationError, InvalidHashError, ValueError, TypeError):
        return False


def create_token(username: str, role: str) -> str:
    if not settings.cronos_auth_secret:
        raise ValueError("CRONOS_AUTH_SECRET is not set")
    payload = {
        "sub": username,
        "role": role,
        "exp": int((datetime.now(UTC) + timedelta(hours=24)).timestamp()),
    }
    return jwt.encode(payload, settings.cronos_auth_secret, algorithm="HS256")


def decode_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(
            token, settings.cronos_auth_secret, algorithms=["HS256"]
        )
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> TokenPayload:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return decode_token(credentials.credentials)


def _check_rate_limit(username: str) -> None:
    now = datetime.now(UTC)
    attempts = _failed_attempts.get(username, [])
    attempts = [t for t in attempts if t > now - timedelta(minutes=1)]
    if len(attempts) >= RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Too many attempts")


def _record_failed_attempt(username: str) -> None:
    now = datetime.now(UTC)
    if username not in _failed_attempts:
        _failed_attempts[username] = []
    _failed_attempts[username].append(now)


def get_user_from_db(username: str) -> dict[str, Any] | None:
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            select(users_table).where(users_table.c.username == username)
        ).mappings().first()
        return dict(row) if row else None


def create_user_in_db(username: str, password_hash: str, role: str = "operator") -> None:
    engine = get_engine()
    from sqlalchemy import insert
    with engine.begin() as conn:
        conn.execute(
            insert(users_table).values(
                username=username,
                password_hash=password_hash,
                role=role,
            )
        )


def update_user_login(username: str) -> None:
    engine = get_engine()
    from sqlalchemy import update
    with engine.begin() as conn:
        conn.execute(
            update(users_table)
            .where(users_table.c.username == username)
            .values(last_login_at=datetime.now(UTC), failed_attempts=0)
        )


def record_login_failure(username: str) -> None:
    engine = get_engine()
    from sqlalchemy import update
    with engine.begin() as conn:
        row = conn.execute(
            select(users_table.c.failed_attempts).where(users_table.c.username == username)
        ).scalar()
        attempts = (row or 0) + 1
        stmt = update(users_table).where(users_table.c.username == username).values(
            failed_attempts=attempts,
        )
        if attempts >= LOCKOUT_THRESHOLD:
            stmt = stmt.values(
                locked_until=datetime.now(UTC) + timedelta(minutes=LOCKOUT_WINDOW_MINUTES)
            )
        conn.execute(stmt)


def is_account_locked(username: str) -> bool:
    user = get_user_from_db(username)
    if not user:
        return False
    locked_until = user.get("locked_until")
    return bool(locked_until and locked_until > datetime.now(UTC))

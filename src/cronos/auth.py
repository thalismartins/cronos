from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from cronos.config import settings

# ruff: noqa: B008

_ph = PasswordHasher()
_bearer = HTTPBearer(auto_error=False)

RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX_ATTEMPTS = 5
_failed_attempts: dict[str, list[datetime]] = {}


class TokenPayload(BaseModel):
    sub: str
    role: str
    exp: datetime


def _check_rate_limit(identifier: str) -> None:
    now = datetime.now(UTC)
    attempts = _failed_attempts.setdefault(identifier, [])
    attempts[:] = [t for t in attempts if now - t < timedelta(seconds=RATE_LIMIT_WINDOW)]
    if len(attempts) >= RATE_LIMIT_MAX_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Too many attempts. Try again later.")


def _record_failed_attempt(identifier: str) -> None:
    _failed_attempts.setdefault(identifier, []).append(datetime.now(UTC))


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _ph.verify(hashed, plain)
    except (VerificationError, InvalidHashError, ValueError, TypeError):
        return False


def hash_password(plain: str) -> str:
    return _ph.hash(plain)


def create_token(user: str, role: str = "operator") -> str:
    secret = settings.cronos_auth_secret
    if not secret or len(secret) < 32:
        raise ValueError("CRONOS_AUTH_SECRET must be at least 32 characters")
    payload = {
        "sub": user,
        "role": role,
        "exp": datetime.now(UTC) + timedelta(hours=8),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_token(token: str) -> TokenPayload:
    secret = settings.cronos_auth_secret
    try:
        data = jwt.decode(token, secret, algorithms=["HS256"])
        return TokenPayload(**data)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> TokenPayload:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return decode_token(credentials.credentials)


async def get_admin_user(current: TokenPayload = Depends(get_current_user)) -> TokenPayload:
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return current

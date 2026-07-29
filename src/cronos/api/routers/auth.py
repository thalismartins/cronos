from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from cronos.auth import (
    TokenPayload,
    _check_rate_limit,
    _record_failed_attempt,
    create_token,
    get_current_user,
    hash_password,
    verify_password,
)
from cronos.config import settings

# ruff: noqa: B008

router = APIRouter()

# Simple user store (replace with DB in production)
_users: dict[str, str] = {}
_admins: set[str] = set()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    role: str
    user: str


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "operator"


@router.post("/auth/login")
async def login(req: LoginRequest) -> LoginResponse:
    _check_rate_limit(req.username)
    hashed = _users.get(req.username)
    if not hashed or not verify_password(req.password, hashed):
        _record_failed_attempt(req.username)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    role = "admin" if req.username in _admins else "operator"
    token = create_token(req.username, role)
    return LoginResponse(token=token, role=role, user=req.username)


@router.post("/auth/setup")
async def setup_admin(req: UserCreate) -> dict:
    if not settings.cronos_auth_secret:
        raise HTTPException(status_code=400, detail="Set CRONOS_AUTH_SECRET first")
    if _users:
        raise HTTPException(status_code=400, detail="Already initialized")
    _users[req.username] = hash_password(req.password)
    if req.role == "admin":
        _admins.add(req.username)
    return {"message": "Admin user created"}


@router.post("/auth/users")
async def create_user(
    req: UserCreate,
    current: TokenPayload = Depends(get_current_user),
) -> dict:
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    _users[req.username] = hash_password(req.password)
    if req.role == "admin":
        _admins.add(req.username)
    return {"message": f"User {req.username} created"}


@router.get("/auth/me")
async def me(current: TokenPayload = Depends(get_current_user)) -> TokenPayload:
    return current

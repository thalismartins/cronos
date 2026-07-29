from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

# ruff: noqa: B008
from pydantic import BaseModel

from cronos.auth import (
    TokenPayload,
    _check_rate_limit,
    _record_failed_attempt,
    create_token,
    create_user_in_db,
    get_current_user,
    get_user_from_db,
    hash_password,
    is_account_locked,
    record_login_failure,
    update_user_login,
    verify_password,
)
from cronos.config import settings

router = APIRouter()


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
    if is_account_locked(req.username):
        raise HTTPException(status_code=423, detail="Account locked")
    user = get_user_from_db(req.username)
    if not user or not verify_password(req.password, user["password_hash"]):
        _record_failed_attempt(req.username)
        record_login_failure(req.username)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account disabled")
    update_user_login(req.username)
    role = user["role"]
    token = create_token(req.username, role)
    return LoginResponse(token=token, role=role, user=req.username)


@router.post("/auth/setup")
async def setup_admin(req: UserCreate) -> dict:
    if not settings.cronos_auth_secret:
        raise HTTPException(status_code=400, detail="Set CRONOS_AUTH_SECRET first")
    existing = get_user_from_db(req.username)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    create_user_in_db(req.username, hash_password(req.password), req.role or "admin")
    return {"message": "Admin user created"}


@router.post("/auth/users")
async def create_user(
    req: UserCreate,
    current: TokenPayload = Depends(get_current_user),
) -> dict:
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    existing = get_user_from_db(req.username)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    create_user_in_db(req.username, hash_password(req.password), req.role or "operator")
    return {"message": f"User {req.username} created"}


@router.get("/auth/me")
async def me(current: TokenPayload = Depends(get_current_user)) -> TokenPayload:
    return current

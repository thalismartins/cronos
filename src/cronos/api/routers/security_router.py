from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/security/certificates")
async def certificates():
    return {"data": []}


@router.get("/security/audit-logs")
async def audit_logs():
    return {"data": []}


@router.get("/security/anomalies")
async def anomalies():
    return {"data": []}


@router.get("/security/kms-servers")
async def kms_servers():
    return {"data": []}

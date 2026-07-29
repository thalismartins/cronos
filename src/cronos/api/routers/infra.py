from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from cronos.persistence.db import get_readonly_engine

router = APIRouter()


@router.get("/appliances")
async def appliances():
    engine = get_readonly_engine()
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT id AS ext_id, alias AS name FROM masters")).mappings().fetchall()
        return [dict(r) for r in rows]


@router.get("/clusters")
async def clusters():
    return []


@router.get("/media-servers")
async def media_servers():
    return []


@router.get("/media/")
async def media_list():
    return {"data": []}


@router.get("/drives/")
async def drives():
    return {"data": []}


@router.get("/services/")
async def services_list():
    return {"data": []}


@router.get("/services/health")
async def services_health():
    engine = get_readonly_engine()
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM masters")).scalar() or 0
        return {
            "generated_at": None,
            "total_services": total,
            "running": total,
            "not_running": 0,
            "critical_down": 0,
            "items": [],
        }


@router.get("/catalog/status")
async def catalog_status():
    return {"data": []}


@router.get("/slp/backlog")
async def slp_backlog():
    return {"data": []}


@router.get("/licensing/entitlements")
async def licensing_entitlements():
    return {"data": []}


@router.get("/licensing/capacity")
async def licensing_capacity():
    return {"data": [], "clients": []}

from __future__ import annotations

from fastapi import APIRouter, Query
from sqlalchemy import select, text

from cronos.persistence.db import get_readonly_engine
from cronos.persistence.schema import disk_pools

router = APIRouter()


@router.get("/storage/disk-pools")
async def storage_disk_pools():
    engine = get_readonly_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            select(disk_pools).order_by(disk_pools.c.name)
        ).mappings().fetchall()
        return {"data": [dict(r) for r in rows]}


@router.get("/storage/disk-pools/history")
async def storage_pool_history(days: int = Query(60)):
    engine = get_readonly_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT * FROM disk_pools
                WHERE collected_at >= NOW() - INTERVAL '1 day' * :days
                ORDER BY collected_at
            """),
            {"days": days},
        ).mappings().fetchall()
        return {"data": [dict(r) for r in rows]}


@router.get("/storage/immutability")
async def storage_immutability():
    engine = get_readonly_engine()
    with engine.connect() as conn:
        total_units = conn.execute(
            text("SELECT COUNT(*) AS cnt FROM disk_pools")
        ).scalar() or 0
        return {
            "total_storage_units": total_units,
            "worm_capable_units": 0,
            "worm_enabled_units": 0,
            "total_disk_pools": total_units,
            "worm_capable_pools": 0,
        }


@router.get("/storage/servers")
async def storage_servers():
    engine = get_readonly_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT DISTINCT master_id, ext_id, name FROM disk_pools")
        ).mappings().fetchall()
        return [dict(r) for r in rows]


@router.get("/storage/units")
async def storage_units():
    return []


@router.get("/storage/capacity-forecast")
async def storage_capacity_forecast():
    engine = get_readonly_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT master_id, ext_id AS disk_pool_ext_id, name,
                       used_capacity_gb AS used_gb,
                       total_capacity_gb AS total_gb,
                       CASE WHEN total_capacity_gb > 0
                           THEN (used_capacity_gb / total_capacity_gb) * 100
                           ELSE 0 END AS used_pct
                FROM disk_pools
            """)
        ).mappings().fetchall()
        return {"warn_days": 30, "generated_at": None, "data": [dict(r) for r in rows]}

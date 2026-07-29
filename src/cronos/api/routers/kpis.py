from __future__ import annotations

from cachetools import TTLCache
from fastapi import APIRouter, Query
from sqlalchemy import text

from cronos.persistence.db import get_readonly_engine
from cronos.persistence.repositories import get_kpis

router = APIRouter()
_cache: TTLCache = TTLCache(maxsize=100, ttl=60)


@router.get("/kpis/performance")
async def kpis_performance(master: str | None = Query(None)):
    engine = get_readonly_engine()
    return get_kpis(engine, master)


@router.get("/kpis/storage")
async def kpis_storage(master: str | None = Query(None)):
    engine = get_readonly_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT
                    master_id,
                    COUNT(*) AS pool_count,
                    SUM(total_capacity_gb) AS total_capacity,
                    SUM(used_capacity_gb) AS used_capacity,
                    AVG(dedup_ratio) AS avg_dedup
                FROM disk_pools
                WHERE (:master IS NULL OR master_id = :master)
                GROUP BY master_id
            """),
            {"master": master},
        ).fetchall()
        return [dict(r._mapping) for r in rows]


@router.get("/kpis/operations")
async def kpis_operations():
    engine = get_readonly_engine()
    with engine.connect() as conn:
        master_count = conn.execute(text("SELECT COUNT(*) FROM masters")).scalar()
        collector_count = conn.execute(text("SELECT COUNT(*) FROM collectors")).scalar()
        asset_count = conn.execute(text("SELECT COUNT(*) FROM assets")).scalar()
        return {
            "master_count": master_count,
            "collector_count": collector_count,
            "asset_count": asset_count,
        }


@router.get("/kpis/resilience")
async def kpis_resilience():
    engine = get_readonly_engine()
    with engine.connect() as conn:
        total_jobs = conn.execute(text("SELECT COUNT(*) FROM jobs")).scalar()
        failed_jobs = conn.execute(text("SELECT COUNT(*) FROM jobs WHERE status_code > 1")).scalar()
        return {
            "total_jobs": total_jobs,
            "failed_jobs": failed_jobs,
            "fail_rate": round((failed_jobs / total_jobs * 100) if total_jobs else 0, 2),
        }

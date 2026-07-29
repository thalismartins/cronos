from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Query
from sqlalchemy import text

from cronos.persistence.db import get_readonly_engine

router = APIRouter()


@router.get("/collection-runs")
async def list_collection_runs(
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
):
    engine = get_readonly_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT id, collector_id, master_id, start_time, end_time, status,
                       error_message, records_collected
                FROM collection_runs
                ORDER BY start_time DESC
                LIMIT :limit OFFSET :offset
            """),
            {"limit": limit, "offset": offset},
        ).fetchall()
        return {"data": [dict(r._mapping) for r in rows]}


@router.get("/collection-runs/health")
async def collection_health():
    engine = get_readonly_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT
                    master_id,
                    MAX(start_time) AS last_run_at,
                    (SELECT status FROM collection_runs cr2
                     WHERE cr2.master_id = collection_runs.master_id
                     ORDER BY start_time DESC LIMIT 1) AS last_run_status,
                    MAX(CASE WHEN status = 'success' THEN start_time END) AS last_success_at
                FROM collection_runs
                GROUP BY master_id
            """)
        ).mappings().fetchall()
        data = []
        for r in rows:
            d = dict(r)
            last = d.get("last_run_at")
            lag = None
            if last:
                lag = int((datetime.now(UTC) - last).total_seconds())
            is_stale = lag is not None and lag > 28800  # 8h
            d["lag_seconds"] = lag
            d["is_stale"] = is_stale
            data.append(d)
        return {
            "stale_threshold_hours": 8,
            "generated_at": datetime.now(UTC).isoformat(),
            "total_masters": len(data),
            "stale_masters": sum(1 for d in data if d["is_stale"]),
            "last_run_failed_masters": sum(1 for d in data if d.get("last_run_status") == "failed"),
            "data": data,
        }

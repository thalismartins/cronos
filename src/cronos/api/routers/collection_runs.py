from __future__ import annotations

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
        return [dict(r._mapping) for r in rows]

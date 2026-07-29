from __future__ import annotations

from fastapi import APIRouter, Query
from sqlalchemy import text

from cronos.persistence.db import get_readonly_engine

router = APIRouter()


@router.get("/jobs")
async def list_jobs(
    master: str | None = Query(None),
    status_code: int | None = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
):
    engine = get_readonly_engine()
    conditions = []
    params = {"limit": limit, "offset": offset}
    if master:
        conditions.append("master_id = :master")
        params["master"] = master
    if status_code is not None:
        conditions.append("status_code = :sc")
        params["sc"] = status_code

    where = " AND ".join(conditions) if conditions else "TRUE"
    with engine.connect() as conn:
        rows = conn.execute(
            text(f"""
                SELECT id, master_id, ext_id, job_type, state, status_code,
                       policy_name, start_time, end_time, duration_seconds
                FROM jobs
                WHERE {where}
                ORDER BY start_time DESC
                LIMIT :limit OFFSET :offset
            """),
            params,
        ).fetchall()
        return [dict(r._mapping) for r in rows]


@router.get("/jobs/summary")
async def jobs_summary(master: str | None = Query(None)):
    engine = get_readonly_engine()
    params = {}
    condition = ""
    if master:
        condition = "WHERE master_id = :master"
        params["master"] = master

    with engine.connect() as conn:
        rows = conn.execute(
            text(f"""
                SELECT
                    status_code,
                    COUNT(*) AS count,
                    MIN(start_time) AS first_seen,
                    MAX(start_time) AS last_seen
                FROM jobs
                {condition}
                GROUP BY status_code
                ORDER BY count DESC
                LIMIT 20
            """),
            params,
        ).fetchall()
        return [dict(r._mapping) for r in rows]

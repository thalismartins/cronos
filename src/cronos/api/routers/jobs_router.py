from __future__ import annotations

from fastapi import APIRouter, Query
from sqlalchemy import func, select, text

from cronos.persistence.db import get_readonly_engine
from cronos.persistence.schema import jobs

router = APIRouter()


@router.get("/jobs/")
async def list_jobs(
    window: str = Query("24h"),
    limit: int = Query(200),
    cursor: str | None = Query(None),
    master_id: str | None = Query(None),
    status_code: int | None = Query(None),
    job_type: str | None = Query(None),
    policy_type: str | None = Query(None),
    state: int | None = Query(None),
    only_failed: bool | None = Query(None),
):
    engine = get_readonly_engine()
    with engine.connect() as conn:
        base = select(jobs).order_by(jobs.c.start_time.desc().nullslast()).limit(limit)
        if cursor:
            base = base.where(jobs.c.id > int(cursor))
        if master_id:
            ids = [m.strip() for m in master_id.split(",") if m.strip()]
            base = base.where(jobs.c.master_id.in_(ids))
        if status_code is not None:
            base = base.where(jobs.c.status_code == status_code)
        if job_type:
            base = base.where(jobs.c.job_type == job_type)
        if policy_type:
            base = base.where(jobs.c.policy_type == policy_type)
        if state is not None:
            base = base.where(jobs.c.state == str(state))
        if only_failed:
            base = base.where(jobs.c.status_code > 1)

        rows = conn.execute(base).mappings().fetchall()
        data = [dict(r) for r in rows]
        if data:
            for r in data:
                if r.get("start_time"):
                    r["start_time"] = r["start_time"].isoformat()
                if r.get("end_time"):
                    r["end_time"] = r["end_time"].isoformat()
                if r.get("collected_at"):
                    r["collected_at"] = r["collected_at"].isoformat()
        next_cursor = str(data[-1]["id"]) if len(data) == limit else None
        return {"data": data, "next_cursor": next_cursor}


@router.get("/jobs/summary")
async def jobs_summary(
    window: str = Query("24h"),
    master_id: str | None = Query(None),
    status_code: int | None = Query(None),
    job_type: str | None = Query(None),
    policy_type: str | None = Query(None),
    state: int | None = Query(None),
    only_failed: bool | None = Query(None),
):
    engine = get_readonly_engine()
    with engine.connect() as conn:
        base = select(func.count()).select_from(jobs)
        mid_cond = None
        if master_id:
            ids = [m.strip() for m in master_id.split(",") if m.strip()]
            mid_cond = jobs.c.master_id.in_(ids)
            base = base.where(mid_cond)
        if status_code is not None:
            base = base.where(jobs.c.status_code == status_code)
        if job_type:
            base = base.where(jobs.c.job_type == job_type)
        if policy_type:
            base = base.where(jobs.c.policy_type == policy_type)
        if state is not None:
            base = base.where(jobs.c.state == str(state))
        if only_failed:
            base = base.where(jobs.c.status_code > 1)

        filt = [jobs.c.status_code > 1]
        if mid_cond is not None:
            filt.append(mid_cond)
        total = conn.execute(base).scalar() or 0
        failures = conn.execute(select(func.count()).select_from(jobs).where(*filt)).scalar() or 0
        filt_a = [jobs.c.state == "1"]
        if mid_cond is not None:
            filt_a.append(mid_cond)
        active = conn.execute(select(func.count()).select_from(jobs).where(*filt_a)).scalar() or 0
        filt_q = [jobs.c.state == "0"]
        if mid_cond is not None:
            filt_q.append(mid_cond)
        queued = conn.execute(select(func.count()).select_from(jobs).where(*filt_q)).scalar() or 0

        return {"total": total, "failures": failures, "active": active, "queued": queued}


@router.get("/kpis/status-codes")
async def kpis_status_codes(window: str = Query("24h"), limit: int = Query(8)):
    engine = get_readonly_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT status_code, COUNT(*) AS count
                FROM jobs
                GROUP BY status_code
                ORDER BY count DESC
                LIMIT :lim
            """),
            {"lim": limit},
        ).mappings().fetchall()
        top_codes = [dict(r) for r in rows]
        for c in top_codes:
            if c["status_code"] == 0:
                c["message"] = "Success"
            elif c["status_code"] == 1:
                c["message"] = "Partial success"
            else:
                c["message"] = f"Error code {c['status_code']}"
        return {"top_codes": top_codes}


@router.get("/kpis/jobs")
async def kpis_jobs(window: str = Query("24h")):
    engine = get_readonly_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT
                    COALESCE(job_type, 'Unknown') AS job_type,
                    COALESCE(policy_type, 'Unknown') AS policy_type,
                    COUNT(*) FILTER (WHERE status_code = 0) AS successful_count,
                    COUNT(*) FILTER (WHERE status_code > 1) AS failed_count,
                    COUNT(*) FILTER (WHERE status_code = 1) AS partial_count
                FROM jobs
                GROUP BY job_type, policy_type
                ORDER BY successful_count DESC
            """),
        ).mappings().fetchall()
        return {"window": window, "stats": [dict(r) for r in rows]}

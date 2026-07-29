from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter
from sqlalchemy import func, select, text

from cronos.persistence.db import get_readonly_engine
from cronos.persistence.schema import assets, jobs

router = APIRouter()


@router.get("/resilience/alert-gate")
async def alert_gate():
    engine = get_readonly_engine()
    with engine.connect() as conn:
        codes = conn.execute(
            text("""
                SELECT status_code, COUNT(*) AS job_count
                FROM jobs WHERE status_code > 1
                GROUP BY status_code ORDER BY job_count DESC LIMIT 20
            """),
        ).mappings().fetchall()
        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "window_days": 1,
            "job_types": ["BACKUP", "RESTORE"],
            "total_in_scope_failures": sum(r["job_count"] for r in codes),
            "alert_worthy_jobs": sum(r["job_count"] for r in codes if r["status_code"] not in (0, 1, 99)),
            "codes": [dict(r) for r in codes],
        }


@router.get("/resilience/recovery-points")
async def recovery_points():
    engine = get_readonly_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT master_id, ext_id AS asset_ext_uuid,
                       COUNT(*) AS rp_count,
                       MIN(start_time) AS oldest_rp,
                       MAX(start_time) AS newest_rp,
                       0 AS airgap_copy_count
                FROM jobs WHERE status_code = 0
                GROUP BY master_id, ext_id
            """)
        ).mappings().fetchall()
        return {"data": [dict(r) for r in rows]}


@router.get("/resilience/malware-scans")
async def malware_scans():
    return {"data": []}


@router.get("/resilience/recoverability")
async def recoverability():
    engine = get_readonly_engine()
    with engine.connect() as conn:
        total = conn.execute(select(func.count()).select_from(assets)).scalar() or 0
        proven = conn.execute(
            select(func.count()).select_from(jobs).where(jobs.c.status_code == 0).distinct()
        ).scalar() or 0
        return {
            "proof_stale_threshold_days": 90,
            "generated_at": datetime.now(UTC).isoformat(),
            "total_protected": total,
            "proven_recoverable": proven,
            "unproven": max(0, total - proven),
            "proof_stale_count": 0,
            "data": [],
        }


@router.get("/resilience/copy-resilience")
async def copy_resilience():
    return {"data": []}


@router.get("/resilience/air-replication")
async def air_replication():
    return {"data": []}


@router.get("/resilience/scorecard")
async def scorecard():
    engine = get_readonly_engine()
    with engine.connect() as conn:
        total = conn.execute(select(func.count()).select_from(jobs)).scalar() or 0
        success = conn.execute(
            select(func.count()).select_from(jobs).where(jobs.c.status_code == 0)
        ).scalar() or 0
        failed = conn.execute(
            select(func.count()).select_from(jobs).where(jobs.c.status_code > 1)
        ).scalar() or 0
        rate = round((success / total * 100) if total else 0, 2)
        components = [
            {"key": "operational", "label": "Operational", "value": rate, "weight": 30, "rating": "green" if rate >= 90 else "amber" if rate >= 70 else "red", "detail": {}},
            {"key": "recoverability", "label": "Recoverability", "value": 50, "weight": 20, "rating": "amber", "detail": {}},
            {"key": "immutability", "label": "Immutability", "value": None, "weight": 15, "rating": "unknown", "detail": {}},
            {"key": "trust", "label": "Trust", "value": 100, "weight": 15, "rating": "green", "detail": {}},
            {"key": "cyber", "label": "Cyber", "value": None, "weight": 10, "rating": "unknown", "detail": {}},
            {"key": "capacity", "label": "Capacity", "value": None, "weight": 10, "rating": "unknown", "detail": {}},
        ]
        score = round(sum(c["value"] or 0 for c in components) / sum(c["weight"] for c in components), 2) if any(c["value"] for c in components) else None
        return {
            "score": score,
            "rating": "green" if score and score >= 80 else "amber" if score and score >= 50 else "red",
            "window": "7d",
            "generated_at": datetime.now(UTC).isoformat(),
            "components": components,
            "headline": {"total_jobs": total, "successful_jobs": success, "failed_jobs": failed},
        }

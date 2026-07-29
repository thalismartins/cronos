from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from cronos.persistence.db import get_readonly_engine

router = APIRouter()


@router.get("/masters")
async def list_masters():
    engine = get_readonly_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT
                    m.*,
                    fs.sla_hours,
                    fs.sla_violated,
                    CASE
                        WHEN m.last_collected_at IS NULL THEN 'never'
                        WHEN NOW() - m.last_collected_at > (fs.sla_hours || ' hours')::interval THEN 'violated'
                        ELSE 'ok'
                    END AS freshness_status
                FROM masters m
                LEFT JOIN freshness_sla fs ON fs.master_id = m.id
            """)
        ).fetchall()
        return [dict(r._mapping) for r in rows]

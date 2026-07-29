from __future__ import annotations

from fastapi import APIRouter, Query
from sqlalchemy import text

from cronos.persistence.db import get_readonly_engine

router = APIRouter()


@router.get("/assets")
async def list_assets(master: str | None = Query(None)):
    engine = get_readonly_engine()
    params = {}
    condition = ""
    if master:
        condition = "WHERE master_id = :master"
        params["master"] = master

    with engine.connect() as conn:
        rows = conn.execute(
            text(f"""
                SELECT a.*,
                    (SELECT COUNT(*) FROM jobs j
                     WHERE j.asset_ext_uuid = a.ext_uuid
                     AND j.status_code = 0
                     AND j.start_time >= NOW() - INTERVAL '24 hours') AS last_24h_success
                FROM assets a
                {condition}
                ORDER BY a.name
            """),
            params,
        ).fetchall()
        return [dict(r._mapping) for r in rows]

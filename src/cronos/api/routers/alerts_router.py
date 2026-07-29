from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text

from cronos.auth import TokenPayload, get_current_user

# ruff: noqa: B008
from cronos.persistence.db import get_engine
from cronos.services.alerts import evaluate_alerts

router = APIRouter()


@router.get("/alerts")
async def list_alerts(open_only: bool = True):
    engine = get_engine()
    with engine.connect() as conn:
        query = text("""
            SELECT id, master_id, collector_id, rule, severity, message, status,
                   acknowledged_at, resolved_at, created_at
            FROM alerts
            WHERE (:open_only = FALSE OR status = 'open')
            ORDER BY created_at DESC
            LIMIT 100
        """)
        rows = conn.execute(query, {"open_only": open_only}).mappings().fetchall()
        return {"data": [dict(r) for r in rows]}


@router.post("/alerts/evaluate")
async def evaluate(current: TokenPayload = Depends(get_current_user)):
    if current.role not in ("admin", "operator"):
        raise HTTPException(status_code=403, detail="Permission denied")
    engine = get_engine()
    results = evaluate_alerts(engine)
    return {"evaluated": True, "alerts_created": len(results), "results": results}


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int, current: TokenPayload = Depends(get_current_user)):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE alerts SET status = 'acknowledged', acknowledged_at = :now WHERE id = :id"),
            {"id": alert_id, "now": datetime.now(UTC)},
        )
    return {"status": "acknowledged"}

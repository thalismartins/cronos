from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from cronos.persistence.db import get_engine

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/ready")
async def ready():
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except (ConnectionError, RuntimeError) as e:
        return {"status": "not ready", "database": str(e)}

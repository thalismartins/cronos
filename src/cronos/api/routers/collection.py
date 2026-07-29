from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException

from cronos.collector.discovery import discover_collectors
from cronos.collector.registry import registry
from cronos.config import load_collectors_config
from cronos.persistence.db import get_engine
from cronos.persistence.repositories import insert_collection_run, update_collection_run
from cronos.scheduler.engine import _persist_record

router = APIRouter()


@router.post("/collect")
async def trigger_collect_all():
    cfg = load_collectors_config()
    discover_collectors()
    engine = get_engine()
    results = []

    for entry in cfg.get("collectors", []):
        cid = entry.get("id")
        if not entry.get("enabled", True) or cid not in registry:
            continue
        try:
            await _run_collect(engine, cid, entry.get("config", {}))
            results.append({"collector": cid, "status": "triggered"})
        except (ConnectionError, TimeoutError, ValueError) as e:
            results.append({"collector": cid, "status": f"failed: {e}"})

    return {"results": results}


@router.post("/collect/{master_id}")
async def trigger_collect_master(master_id: str):
    cfg = load_collectors_config()
    discover_collectors()
    engine = get_engine()

    for entry in cfg.get("collectors", []):
        cid = entry.get("id")
        masters = entry.get("config", {}).get("masters", [])
        if not any(m.get("alias") == master_id for m in masters):
            continue
        if cid not in registry:
            raise HTTPException(404, f"Collector {cid} not found")

        await _run_collect(engine, cid, entry.get("config", {}))
        return {"collector": cid, "master": master_id, "status": "triggered"}

    raise HTTPException(404, f"Master {master_id} not found")


async def _run_collect(engine, collector_id: str, config: dict) -> None:
    collector_cls = registry[collector_id]
    collector = collector_cls()
    masters = config.get("masters", [{"alias": "default"}])

    for master in masters:
        mid = master.get("alias", "default")
        run_id = insert_collection_run(engine, {
            "collector_id": collector_id,
            "master_id": mid,
            "start_time": datetime.now(UTC),
            "status": "running",
        })

        try:
            from cronos.collector.interface import CollectorState
            state = CollectorState(master_id=mid, collector_id=collector_id, run_id=run_id)
            count = 0
            async for record in collector.collect({"masters": [master]}, state):
                _persist_record(engine, record)
                count += 1

            update_collection_run(engine, run_id, {
                "end_time": datetime.now(UTC),
                "status": "success",
                "records_collected": count,
            })
        except Exception as e:
            update_collection_run(engine, run_id, {
                "end_time": datetime.now(UTC),
                "status": "failed",
                "error_message": str(e),
            })
            raise

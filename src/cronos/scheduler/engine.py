from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from cronos.collector.discovery import discover_collectors
from cronos.collector.registry import registry
from cronos.config import load_collectors_config
from cronos.persistence.db import get_engine
from cronos.persistence.repositories import insert_collection_run, update_collection_run

logger = logging.getLogger(__name__)


def run_scheduler() -> None:
    scheduler = AsyncIOScheduler()
    cfg = load_collectors_config()
    discover_collectors()
    engine = get_engine()

    for entry in cfg.get("collectors", []):
        cid = entry.get("id")
        if not entry.get("enabled", True) or cid not in registry:
            continue

        cron_expr = entry.get("schedule", "0 */6 * * *")
        trigger = CronTrigger.from_cron(cron_expr)

        scheduler.add_job(
            _run_collector_job,
            trigger=trigger,
            args=[cid, entry.get("config", {}), engine],
            id=f"collect_{cid}",
            replace_existing=True,
            name=f"Collector: {cid}",
        )
        logger.info("Scheduled collector %s with CRON: %s", cid, cron_expr)

    logger.info("Scheduler started. Press Ctrl+C to stop.")
    try:
        scheduler.start()
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped.")


async def _run_collector_job(
    collector_id: str,
    config: dict,
    engine,
) -> None:
    collector_cls = registry.get(collector_id)
    if not collector_cls:
        logger.error("Collector %s not found in registry", collector_id)
        return

    masters = config.get("masters", [{"alias": "default"}])
    for master in masters:
        mid = master.get("alias", "default")
        try:
            run_id = insert_collection_run(engine, {
                "collector_id": collector_id,
                "master_id": mid,
                "start_time": datetime.now(UTC),
                "status": "running",
            })

            collector = collector_cls()
            from cronos.collector.interface import CollectorState
            state = CollectorState(master_id=mid, collector_id=collector_id, run_id=run_id)

            records_count = 0
            async for record in collector.collect(
                {"masters": [master]} if "masters" not in config else config,
                state,
            ):
                _persist_record(engine, record)
                records_count += 1

            update_collection_run(engine, run_id, {
                "end_time": datetime.now(UTC),
                "status": "success",
                "records_collected": records_count,
            })
            logger.info("Collector %s | master %s: %d records", collector_id, mid, records_count)

        except (ConnectionError, TimeoutError, OSError) as e:
            logger.error("Collector %s | master %s failed: %s", collector_id, mid, str(e))
            if run_id:
                update_collection_run(engine, run_id, {
                    "end_time": datetime.now(UTC),
                    "status": "failed",
                    "error_message": str(e),
                })


def _persist_record(engine, record) -> None:
    from cronos.persistence.repositories import (
        insert_job,
        upsert_asset,
        upsert_disk_pool,
    )

    payload = record.payload
    if record.category == "job":
        insert_job(engine, {
            "master_id": record.master_id,
            "ext_id": record.ext_id,
            "job_type": payload.get("job_type"),
            "state": payload.get("state"),
            "status_code": payload.get("status_code"),
            "policy_name": payload.get("policy_name"),
            "policy_type": payload.get("policy_type"),
            "asset_ext_uuid": payload.get("asset_ext_uuid"),
            "start_time": payload.get("start_time"),
            "end_time": payload.get("end_time"),
            "duration_seconds": payload.get("duration_seconds"),
            "payload": payload,
        })
    elif record.category == "asset":
        upsert_asset(engine, {
            "master_id": record.master_id,
            "ext_id": record.ext_id,
            "ext_uuid": record.ext_id,
            "name": payload.get("name"),
            "type": payload.get("type"),
            "os": payload.get("os"),
            "payload": payload,
        })
    elif record.category == "disk_pool":
        upsert_disk_pool(engine, {
            "master_id": record.master_id,
            "ext_id": record.ext_id,
            "name": payload.get("name"),
            "total_capacity_gb": payload.get("total_capacity_gb"),
            "used_capacity_gb": payload.get("used_capacity_gb"),
            "dedup_ratio": payload.get("dedup_ratio"),
            "storage_category": payload.get("storage_category"),
            "payload": payload,
        })

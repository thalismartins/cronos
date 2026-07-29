from __future__ import annotations

import logging

from sqlalchemy import Engine

from cronos.collector.interface import Record
from cronos.persistence.repositories import (
    insert_job,
    upsert_asset,
    upsert_disk_pool,
    upsert_policy,
)
from cronos.pipeline.validator import normalize_record, validate_record

logger = logging.getLogger(__name__)

HANDLERS = {
    "job": insert_job,
    "asset": upsert_asset,
    "disk_pool": upsert_disk_pool,
    "policy": upsert_policy,
}

FIELD_MAPPING = {
    "job": {
        "master_id": "master_id",
        "ext_id": "ext_id",
        "job_type": "job_type",
        "state": "state",
        "status_code": "status_code",
        "policy_name": "policy_name",
        "policy_type": "policy_type",
        "asset_ext_uuid": "asset_ext_uuid",
        "start_time": "start_time",
        "end_time": "end_time",
        "duration_seconds": "duration_seconds",
    },
    "asset": {
        "master_id": "master_id",
        "ext_id": "ext_id",
        "ext_uuid": "ext_uuid",
        "name": "name",
        "type": "type",
        "os": "os",
    },
    "disk_pool": {
        "master_id": "master_id",
        "ext_id": "ext_id",
        "name": "name",
        "total_capacity_gb": "total_capacity_gb",
        "used_capacity_gb": "used_capacity_gb",
        "dedup_ratio": "dedup_ratio",
        "storage_category": "storage_category",
    },
    "policy": {
        "master_id": "master_id",
        "ext_id": "ext_id",
        "name": "name",
        "policy_type": "policy_type",
        "active": "active",
    },
}


def route_record(engine: Engine, record: Record) -> None:
    if not validate_record(record):
        logger.warning("Skipping invalid record: %s/%s", record.category, record.ext_id)
        return

    record = normalize_record(record)
    handler = HANDLERS.get(record.category)
    mapping = FIELD_MAPPING.get(record.category)

    if not handler or not mapping:
        logger.warning("No handler for category: %s", record.category)
        return

    data = {"master_id": record.master_id, "ext_id": record.ext_id, "payload": record.payload}
    for payload_key, db_column in mapping.items():
        if payload_key == "master_id" or payload_key == "ext_id":
            continue
        value = record.payload.get(payload_key)
        if value is not None:
            data[db_column] = value

    handler(engine, data)

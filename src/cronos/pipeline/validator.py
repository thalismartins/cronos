from __future__ import annotations

import logging

from cronos.collector.interface import Record

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = {
    "job": ["master_id", "ext_id"],
    "asset": ["master_id", "ext_id"],
    "disk_pool": ["master_id", "ext_id"],
    "policy": ["master_id", "ext_id"],
}


def validate_record(record: Record) -> bool:
    required = REQUIRED_FIELDS.get(record.category, [])
    for field in required:
        if not getattr(record, field, None):
            logger.warning("Record %s/%s missing required field: %s", record.category, record.ext_id, field)
            return False
    return True


def normalize_record(record: Record) -> Record:
    payload = dict(record.payload)
    for key, value in list(payload.items()):
        if isinstance(value, dict) and "gigabytes" in value:
            payload[key] = value["gigabytes"]
        if isinstance(value, str) and value.lower() in ("true", "false"):
            payload[key] = value.lower() == "true"
    record.payload = payload
    return record

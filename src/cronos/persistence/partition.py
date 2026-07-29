from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import Engine, text

logger = logging.getLogger(__name__)



PARTITIONED_TABLES = {
    "jobs": {
        "partition_column": "collected_at",
        "interval": "month",
        "template": "CREATE TABLE IF NOT EXISTS {table}_{ym} PARTITION OF {table} FOR VALUES FROM ('{start}') TO ('{end}')",
    },
    "collection_runs": {
        "partition_column": "start_time",
        "interval": "month",
        "template": "CREATE TABLE IF NOT EXISTS {table}_{ym} PARTITION OF {table} FOR VALUES FROM ('{start}') TO ('{end}')",
    },
}


def ensure_partitions(engine: Engine, months_ahead: int = 3) -> None:
    dialect = engine.dialect.name
    if dialect != "postgresql":
        logger.info("Partitioning not supported on %s; skipping", dialect)
        return

    utcnow = datetime.now(UTC)
    for table, cfg in PARTITIONED_TABLES.items():
        for offset in range(months_ahead):
            dt = utcnow + timedelta(days=30 * offset)
            ym = dt.strftime("%Y%m")
            start = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if end_month := dt.month % 12 + 1:
                end = dt.replace(month=end_month, day=1) if end_month > dt.month else dt.replace(year=dt.year + 1, month=1, day=1)
            else:
                end = dt.replace(year=dt.year + 1, month=1, day=1)

            sql = cfg["template"].format(table=table, ym=ym, start=start.isoformat(), end=end.isoformat())
            with engine.begin() as conn:
                try:
                    conn.execute(text(sql))
                    logger.info("Created partition %s_%s", table, ym)
                except (RuntimeError, OSError, ValueError) as e:
                    estr = str(e).lower()
                    if "already exists" not in estr and "use concurrent" not in estr:
                        logger.warning("Failed to create partition %s_%s: %s", table, ym, e)

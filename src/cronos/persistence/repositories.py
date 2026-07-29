from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import Engine, delete, func, insert, select, text, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

from cronos.persistence.schema import (
    assets,
    collection_runs,
    collectors,
    disk_pools,
    jobs,
    masters,
    policies,
)


def upsert_master(engine: Engine, data: dict[str, Any]) -> None:
    stmt = pg_insert(masters).values(**data)
    stmt = stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={k: v for k, v in data.items() if k != "id"},
    )
    with engine.begin() as conn:
        conn.execute(stmt)


def upsert_collector(engine: Engine, data: dict[str, Any]) -> None:
    stmt = pg_insert(collectors).values(**data)
    stmt = stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={k: v for k, v in data.items() if k != "id"},
    )
    with engine.begin() as conn:
        conn.execute(stmt)


def insert_collection_run(engine: Engine, data: dict[str, Any]) -> int:
    with engine.begin() as conn:
        result = conn.execute(insert(collection_runs).values(**data).returning(collection_runs.c.id))
        return result.scalar_one()


def update_collection_run(engine: Engine, run_id: int, data: dict[str, Any]) -> None:
    with engine.begin() as conn:
        conn.execute(update(collection_runs).where(collection_runs.c.id == run_id).values(**data))


def upsert_asset(engine: Engine, data: dict[str, Any]) -> None:
    stmt = pg_insert(assets).values(**data)
    stmt = stmt.on_conflict_do_update(
        index_elements=["master_id", "ext_id"],
        set_={k: v for k, v in data.items() if k not in ("master_id", "ext_id")},
    )
    with engine.begin() as conn:
        conn.execute(stmt)


def insert_job(engine: Engine, data: dict[str, Any]) -> None:
    stmt = pg_insert(jobs).values(**data)
    stmt = stmt.on_conflict_do_update(
        index_elements=["master_id", "ext_id"],
        set_={k: v for k, v in data.items() if k not in ("master_id", "ext_id")},
    )
    with engine.begin() as conn:
        conn.execute(stmt)


def upsert_disk_pool(engine: Engine, data: dict[str, Any]) -> None:
    stmt = pg_insert(disk_pools).values(**data)
    stmt = stmt.on_conflict_do_update(
        index_elements=["master_id", "ext_id"],
        set_={k: v for k, v in data.items() if k not in ("master_id", "ext_id")},
    )
    with engine.begin() as conn:
        conn.execute(stmt)


def upsert_policy(engine: Engine, data: dict[str, Any]) -> None:
    stmt = pg_insert(policies).values(**data)
    stmt = stmt.on_conflict_do_update(
        index_elements=["master_id", "ext_id"],
        set_={k: v for k, v in data.items() if k not in ("master_id", "ext_id")},
    )
    with engine.begin() as conn:
        conn.execute(stmt)


def build_rollups(engine: Engine) -> None:
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO job_kpi_daily (master_id, day, total_jobs, success_jobs, fail_jobs, partial_jobs)
            SELECT
                master_id,
                DATE(start_time) AS day,
                COUNT(*) AS total_jobs,
                COUNT(*) FILTER (WHERE status_code = 0) AS success_jobs,
                COUNT(*) FILTER (WHERE status_code > 1) AS fail_jobs,
                COUNT(*) FILTER (WHERE status_code = 1) AS partial_jobs
            FROM jobs
            WHERE start_time >= NOW() - INTERVAL '7 days'
            GROUP BY master_id, DATE(start_time)
            ON CONFLICT (master_id, day) DO NOTHING
        """))


def prune_data(engine: Engine, retention_days: int = 90) -> None:
    cutoff = datetime.now(UTC) - timedelta(days=retention_days)
    with engine.begin() as conn:
        conn.execute(delete(jobs).where(jobs.c.collected_at < cutoff))
        conn.execute(delete(collection_runs).where(collection_runs.c.start_time < cutoff))


def get_jobs_count(engine: Engine, master_id: str | None = None) -> int:
    query = select(func.count()).select_from(jobs)
    if master_id:
        query = query.where(jobs.c.master_id == master_id)
    with engine.connect() as conn:
        return conn.execute(query).scalar() or 0


def get_kpis(engine: Engine, master_id: str | None = None) -> dict[str, Any]:
    with engine.connect() as conn:
        total = conn.execute(
            select(func.count()).select_from(jobs)
        ).scalar() or 0

        success = conn.execute(
            select(func.count()).select_from(jobs).where(jobs.c.status_code == 0)
        ).scalar() or 0

        failed = conn.execute(
            select(func.count()).select_from(jobs).where(jobs.c.status_code > 1)
        ).scalar() or 0

        return {
            "total_jobs": total,
            "success_jobs": success,
            "fail_jobs": failed,
            "success_rate": round((success / total * 100) if total else 0, 2),
        }

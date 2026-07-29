from __future__ import annotations

from datetime import UTC, datetime

from cronos.persistence.repositories import (
    get_jobs_count,
    get_kpis,
    insert_collection_run,
    insert_job,
    update_collection_run,
    upsert_asset,
    upsert_collector,
    upsert_master,
)


def test_upsert_master(engine):
    upsert_master(engine, {"id": "m1", "alias": "Test Master", "collector_id": "demo"})
    assert get_jobs_count(engine) == 0


def test_upsert_collector(engine):
    upsert_collector(engine, {"id": "demo", "enabled": 1, "schedule_cron": "0 * * * *"})
    # Verify by checking we can read back (no error)


def test_insert_collection_run(engine):
    rid = insert_collection_run(engine, {
        "collector_id": "demo",
        "master_id": "m1",
        "start_time": datetime.now(UTC),
        "status": "running",
    })
    assert rid is not None
    assert rid > 0

    update_collection_run(engine, rid, {
        "end_time": datetime.now(UTC),
        "status": "success",
    })


def test_upsert_asset(engine):
    upsert_asset(engine, {
        "master_id": "m1",
        "ext_id": "asset-1",
        "ext_uuid": "uuid-1",
        "name": "Test Asset",
        "type": "Linux",
    })


def test_insert_job(engine):
    insert_job(engine, {
        "master_id": "m1",
        "ext_id": "job-1",
        "job_type": "BACKUP",
        "state": "done",
        "status_code": 0,
        "start_time": datetime.now(UTC),
    })
    assert get_jobs_count(engine) == 1
    assert get_jobs_count(engine, "m1") == 1


def test_get_kpis(engine):
    kpis = get_kpis(engine)
    assert kpis["total_jobs"] == 0
    assert kpis["success_rate"] == 0.0

    insert_job(engine, {
        "master_id": "m1", "ext_id": "j1", "status_code": 0,
        "start_time": datetime.now(UTC),
    })
    insert_job(engine, {
        "master_id": "m1", "ext_id": "j2", "status_code": 2,
        "start_time": datetime.now(UTC),
    })
    kpis = get_kpis(engine)
    assert kpis["total_jobs"] == 2
    assert kpis["success_jobs"] == 1
    assert kpis["fail_jobs"] == 1
    assert kpis["success_rate"] == 50.0

from __future__ import annotations

import random
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import Engine

from cronos.persistence.repositories import (
    build_rollups,
    insert_job,
    upsert_asset,
    upsert_disk_pool,
    upsert_master,
    upsert_policy,
)


def generate_demo_data(engine: Engine) -> None:
    utcnow = datetime.now(UTC)

    # Masters
    masters_data = [
        {"id": "prod-bu-01", "alias": "Production NBU 01", "collector_id": "netbackup", "family": "11.x"},
        {"id": "prod-bu-02", "alias": "Production NBU 02", "collector_id": "netbackup", "family": "10.x"},
        {"id": "dr-site-01", "alias": "DR Site NBU", "collector_id": "netbackup", "family": "11.x"},
    ]
    for m in masters_data:
        upsert_master(engine, m)

    # Assets (50 per master)
    asset_types = ["Windows", "Linux", "AIX", "Solaris", "Hyper-V", "VMware"]
    asset_names = [
        "web-server-{i}", "db-server-{i}", "app-server-{i}",
        "file-server-{i}", "dc-{i}", "mail-server-{i}",
    ]

    all_asset_uuids = []
    for master in masters_data:
        for i in range(50):
            ext_uuid = str(uuid.uuid4())
            all_asset_uuids.append((master["id"], ext_uuid))
            upsert_asset(engine, {
                "master_id": master["id"],
                "ext_id": ext_uuid,
                "ext_uuid": ext_uuid,
                "name": random.choice(asset_names).format(i=i),
                "type": random.choice(asset_types),
                "os": random.choice(["Windows Server 2022", "RHEL 9", "Ubuntu 24.04", "AIX 7.3"]),
            })

    # Jobs (2000 per master over 30 days)
    job_types = ["BACKUP", "RESTORE", "ARCHIVE", "VALIDATE", "DUPLICATION"]
    policy_types = ["FULL", "INCR", "DIFF", "LOG"]

    for master_id, _ in masters_data:
        for day_offset in range(30):
            day = utcnow - timedelta(days=day_offset)
            for _ in range(random.randint(40, 100)):
                start = day + timedelta(
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                )
                duration = random.randint(60, 7200)
                end = start + timedelta(seconds=duration)
                status_code = random.choices(
                    [0, 0, 0, 0, 1, 2, 5, 6, 13, 25, 50, 84, 96, 100, 150, 196, 200],
                    weights=[40, 30, 10, 5, 5, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                )[0]
                state = "done" if status_code < 2 else random.choice(["failed", "partially_successful"])

                insert_job(engine, {
                    "master_id": master_id,
                    "ext_id": f"JOB-{master_id}-{int(start.timestamp())}-{random.randint(100, 999)}",
                    "job_type": random.choice(job_types),
                    "state": state,
                    "status_code": status_code,
                    "policy_name": f"Policy-{random.choice(['Daily', 'Weekly', 'Monthly'])}-{random.randint(1, 20)}",
                    "policy_type": random.choice(policy_types),
                    "asset_ext_uuid": random.choice(all_asset_uuids)[1],
                    "parent_job_id": None,
                    "start_time": start,
                    "end_time": end,
                    "duration_seconds": duration,
                })

    # Disk pools (5 per master)
    pool_names = ["DataDomain-{i}", "MSDP-{i}", "CloudBucket-{i}", "TapeLib-{i}", "PureDisk-{i}"]
    categories = ["on_prem", "on_prem", "cloud", "tape", "on_prem"]
    for master_id, _ in masters_data:
        for i in range(5):
            total = random.choice([5000, 10000, 20000, 50000, 100000])
            used = total * random.uniform(0.3, 0.85)
            upsert_disk_pool(engine, {
                "master_id": master_id,
                "ext_id": f"POOL-{master_id}-{i}",
                "name": pool_names[i].format(i=i),
                "total_capacity_gb": total,
                "used_capacity_gb": round(used, 2),
                "dedup_ratio": round(random.uniform(1.5, 8.0), 2),
                "storage_category": categories[i],
            })

    # Policies (20 per master)
    for master_id, _ in masters_data:
        for i in range(20):
            upsert_policy(engine, {
                "master_id": master_id,
                "ext_id": f"POL-{master_id}-{i}",
                "name": f"Policy-{random.choice(['Production', 'Critical', 'Standard', 'Compliance'])}-{i}",
                "policy_type": random.choice(policy_types),
                "active": random.choice([1, 1, 1, 0]),
            })

    build_rollups(engine)

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, AsyncGenerator

from cronos.collector.interface import Collector, CollectorState, Record


class DemoCollector(Collector):
    @property
    def id(self) -> str:
        return "demo"

    def capabilities(self) -> list[str]:
        return ["jobs", "assets", "storage", "policies"]

    def config_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "masters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "alias": {"type": "string"},
                        },
                    },
                },
            },
        }

    def validate_config(self, config: dict[str, Any]) -> bool:
        masters = config.get("masters", [])
        return len(masters) > 0

    async def collect(
        self, config: dict[str, Any], state: CollectorState
    ) -> AsyncGenerator[Record, None]:
        utcnow = datetime.now(timezone.utc)

        masters = config.get("masters", [{"alias": "demo-master"}])
        for m in masters:
            mid = m.get("alias", "demo-master")

            # Generate jobs
            for _ in range(random.randint(5, 20)):
                start = utcnow - timedelta(hours=random.randint(0, 48))
                duration = random.randint(60, 3600)
                status = random.choices(
                    [0, 0, 0, 1, 2, 5, 6],
                    weights=[50, 20, 10, 8, 7, 3, 2],
                )[0]

                yield Record(
                    category="job",
                    master_id=mid,
                    ext_id=f"DEMO-{uuid.uuid4().hex[:12]}",
                    payload={
                        "job_type": random.choice(["BACKUP", "RESTORE", "ARCHIVE"]),
                        "state": "done" if status < 2 else "failed",
                        "status_code": status,
                        "policy_type": random.choice(["FULL", "INCR", "DIFF"]),
                        "start_time": start.isoformat(),
                        "end_time": (start + timedelta(seconds=duration)).isoformat(),
                        "duration_seconds": duration,
                    },
                    event_time=start,
                )

            # Generate assets
            for i in range(3):
                ext_uuid = uuid.uuid4().hex
                yield Record(
                    category="asset",
                    master_id=mid,
                    ext_id=ext_uuid,
                    payload={
                        "name": f"demo-srv-{i}",
                        "type": random.choice(["Windows", "Linux", "VMware"]),
                        "os": random.choice(["Windows Server 2022", "RHEL 9"]),
                    },
                )

            # Generate disk pools
            for i in range(2):
                total = random.choice([10000, 50000, 100000])
                used = total * random.uniform(0.3, 0.8)
                yield Record(
                    category="disk_pool",
                    master_id=mid,
                    ext_id=f"pool-{mid}-{i}",
                    payload={
                        "name": f"Pool-{i}",
                        "total_capacity_gb": total,
                        "used_capacity_gb": round(used, 2),
                        "dedup_ratio": round(random.uniform(2.0, 6.0), 2),
                        "storage_category": random.choice(["on_prem", "cloud"]),
                    },
                )

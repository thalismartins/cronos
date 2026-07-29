from __future__ import annotations

from typing import Any, AsyncGenerator

import httpx

from cronos.collector.interface import Collector, CollectorState, Record


class NetBackupCollector(Collector):
    @property
    def id(self) -> str:
        return "netbackup"

    def capabilities(self) -> list[str]:
        return ["jobs", "assets", "storage", "policies", "media", "slp", "catalog", "malware", "appliances"]

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
                            "base_url": {"type": "string"},
                            "api_key_env": {"type": "string"},
                            "family": {"type": "string", "enum": ["10.x", "11.x"]},
                            "verify_tls": {"type": "boolean"},
                        },
                        "required": ["alias", "base_url", "api_key_env"],
                    },
                },
            },
        }

    def validate_config(self, config: dict[str, Any]) -> bool:
        masters = config.get("masters", [])
        if not masters:
            return False
        return all(m.get("base_url") and m.get("api_key_env") for m in masters)

    async def collect(
        self, config: dict[str, Any], state: CollectorState
    ) -> AsyncGenerator[Record, None]:
        import os

        masters = config.get("masters", [])
        for master in masters:
            alias = master["alias"]
            base_url = master["base_url"].rstrip("/")
            api_key = os.environ.get(master["api_key_env"], "")
            family = master.get("family", "11.x")
            verify_tls = master.get("verify_tls", True)

            headers = {
                "Accept": f"application/vnd.netbackup+json;version={family}",
                "Authorization": f"Bearer {api_key}",
            }

            async with httpx.AsyncClient(
                base_url=base_url, headers=headers, verify=verify_tls, timeout=60.0
            ) as client:
                async for record in self._collect_jobs(client, alias):
                    yield record
                async for record in self._collect_assets(client, alias):
                    yield record
                async for record in self._collect_storage(client, alias):
                    yield record
                async for record in self._collect_policies(client, alias):
                    yield record

    async def _collect_jobs(
        self, client: httpx.AsyncClient, master_id: str
    ) -> AsyncGenerator[Record, None]:
        try:
            resp = await client.get("/netbackup/jobs", params={"page[limit]": 100})
            resp.raise_for_status()
            data = resp.json()
            for job in data.get("data", []):
                attrs = job.get("attributes", {})
                yield Record(
                    category="job",
                    master_id=master_id,
                    ext_id=str(job.get("id", "")),
                    payload={
                        "job_type": attrs.get("jobType"),
                        "state": attrs.get("state"),
                        "status_code": attrs.get("status", {}).get("code"),
                        "policy_name": attrs.get("policyName"),
                        "policy_type": attrs.get("policyType"),
                        "start_time": attrs.get("startTime"),
                        "end_time": attrs.get("endTime"),
                        "duration_seconds": attrs.get("elapsed"),
                        "asset_ext_uuid": attrs.get("assetId"),
                    },
                )
        except httpx.HTTPError:
            pass

    async def _collect_assets(
        self, client: httpx.AsyncClient, master_id: str
    ) -> AsyncGenerator[Record, None]:
        try:
            resp = await client.get("/netbackup/assets", params={"page[limit]": 100})
            resp.raise_for_status()
            data = resp.json()
            for asset in data.get("data", []):
                attrs = asset.get("attributes", {})
                yield Record(
                    category="asset",
                    master_id=master_id,
                    ext_id=str(asset.get("id", "")),
                    payload={
                        "ext_uuid": attrs.get("uuid"),
                        "name": attrs.get("displayName"),
                        "type": attrs.get("type"),
                        "os": attrs.get("os"),
                    },
                )
        except httpx.HTTPError:
            pass

    async def _collect_storage(
        self, client: httpx.AsyncClient, master_id: str
    ) -> AsyncGenerator[Record, None]:
        try:
            resp = await client.get("/netbackup/disk-pools", params={"page[limit]": 100})
            resp.raise_for_status()
            data = resp.json()
            for pool in data.get("data", []):
                attrs = pool.get("attributes", {})
                yield Record(
                    category="disk_pool",
                    master_id=master_id,
                    ext_id=str(pool.get("id", "")),
                    payload={
                        "name": attrs.get("name"),
                        "total_capacity_gb": attrs.get("totalCapacity", {}).get("gigabytes"),
                        "used_capacity_gb": attrs.get("usedCapacity", {}).get("gigabytes"),
                        "dedup_ratio": attrs.get("dedupRatio"),
                        "storage_category": attrs.get("storageCategory"),
                    },
                )
        except httpx.HTTPError:
            pass

    async def _collect_policies(
        self, client: httpx.AsyncClient, master_id: str
    ) -> AsyncGenerator[Record, None]:
        try:
            resp = await client.get("/netbackup/policies", params={"page[limit]": 100})
            resp.raise_for_status()
            data = resp.json()
            for policy in data.get("data", []):
                attrs = policy.get("attributes", {})
                yield Record(
                    category="policy",
                    master_id=master_id,
                    ext_id=str(policy.get("id", "")),
                    payload={
                        "name": attrs.get("name"),
                        "policy_type": attrs.get("policyType"),
                        "active": attrs.get("active", True),
                    },
                )
        except httpx.HTTPError:
            pass

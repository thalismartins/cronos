from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class CollectorState:
    master_id: str
    collector_id: str
    run_id: int | None = None
    checkpoint: datetime | None = None


@dataclass
class Record:
    category: str
    master_id: str
    ext_id: str
    payload: dict[str, Any]
    collected_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    event_time: datetime | None = None


class Collector(ABC):
    @property
    @abstractmethod
    def id(self) -> str: ...

    def config_schema(self) -> dict[str, Any]:
        return {"type": "object", "properties": {}}

    def capabilities(self) -> list[str]:
        return []

    def validate_config(self, config: dict[str, Any]) -> bool:
        return True

    @abstractmethod
    async def collect(
        self, config: dict[str, Any], state: CollectorState
    ) -> AsyncGenerator[Record, None]: ...

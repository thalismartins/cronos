from __future__ import annotations

from cronos.collector.interface import Collector

registry: dict[str, type[Collector]] = {}

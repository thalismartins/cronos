from __future__ import annotations

from cronos.collector.interface import Collector, CollectorState, Record
from cronos.collector.registry import registry


class MockCollector(Collector):
    @property
    def id(self) -> str:
        return "mock"

    def capabilities(self) -> list[str]:
        return ["mock_data"]

    async def collect(self, config, state):
        yield Record(
            category="mock",
            master_id=state.master_id,
            ext_id="mock-1",
            payload={"value": 42},
        )


def test_registry():
    registry.clear()
    registry["mock"] = MockCollector
    assert "mock" in registry
    assert issubclass(registry["mock"], Collector)


def test_collector_id():
    c = MockCollector()
    assert c.id == "mock"


def test_capabilities():
    c = MockCollector()
    caps = c.capabilities()
    assert "mock_data" in caps


def test_config_schema():
    c = MockCollector()
    schema = c.config_schema()
    assert isinstance(schema, dict)


def test_validate_config():
    c = MockCollector()
    assert c.validate_config({}) is True


def test_record_creation():
    record = Record(
        category="test",
        master_id="m1",
        ext_id="e1",
        payload={"key": "val"},
    )
    assert record.category == "test"
    assert record.master_id == "m1"
    assert record.payload["key"] == "val"


def test_collector_state():
    state = CollectorState(master_id="m1", collector_id="mock")
    assert state.master_id == "m1"
    assert state.collector_id == "mock"

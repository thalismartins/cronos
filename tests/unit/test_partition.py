from __future__ import annotations

from cronos.persistence.partition import PARTITIONED_TABLES, ensure_partitions


def test_partitioned_tables_defined():
    assert "jobs" in PARTITIONED_TABLES
    assert "collection_runs" in PARTITIONED_TABLES


def test_ensure_partitions_no_crash():
    from sqlalchemy import create_engine
    engine = create_engine("sqlite://")
    ensure_partitions(engine)  # Should not raise even on SQLite
    assert True

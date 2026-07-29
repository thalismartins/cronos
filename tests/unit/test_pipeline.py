from __future__ import annotations

from cronos.collector.interface import Record
from cronos.pipeline.router import route_record
from cronos.pipeline.validator import normalize_record, validate_record


def test_validate_valid_job():
    r = Record(category="job", master_id="m1", ext_id="j1", payload={})
    assert validate_record(r) is True


def test_validate_invalid_record():
    r = Record(category="job", master_id="", ext_id="", payload={})
    assert validate_record(r) is False


def test_normalize_bool_string():
    r = Record(category="job", master_id="m1", ext_id="j1", payload={"active": "true"})
    n = normalize_record(r)
    assert n.payload["active"] is True


def test_normalize_gigabytes():
    r = Record(category="disk_pool", master_id="m1", ext_id="p1", payload={"total": {"gigabytes": 500}})
    n = normalize_record(r)
    assert n.payload["total"] == 500


def test_route_unknown_category(caplog):
    r = Record(category="unknown", master_id="m1", ext_id="x1", payload={})
    from sqlalchemy import create_engine
    engine = create_engine("sqlite://")
    route_record(engine, r)
    # Should not raise, just log a warning
    assert True

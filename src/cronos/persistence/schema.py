from __future__ import annotations

from sqlalchemy import (
    JSON,
    BigInteger,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)

metadata = MetaData()

masters = Table(
    "masters",
    metadata,
    Column("id", String(50), primary_key=True),
    Column("alias", String(200), nullable=False),
    Column("collector_id", String(100), nullable=False),
    Column("family", String(20)),
    Column("state", String(20), server_default="active"),
    Column("freshness_sla_hours", Integer, server_default="8"),
    Column("last_collected_at", DateTime(timezone=True)),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), onupdate=func.now()),
)

collectors = Table(
    "collectors",
    metadata,
    Column("id", String(100), primary_key=True),
    Column("enabled", Integer, server_default="1"),
    Column("schedule_cron", String(100)),
    Column("config", JSON),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

collection_runs = Table(
    "collection_runs",
    metadata,
    Column("id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True),
    Column("collector_id", String(100), nullable=False),
    Column("master_id", String(50), nullable=False),
    Column("start_time", DateTime(timezone=True), nullable=False),
    Column("end_time", DateTime(timezone=True)),
    Column("status", String(20)),
    Column("error_message", Text),
    Column("records_collected", Integer, server_default="0"),
)

Index("ix_collection_runs_master_start", collection_runs.c.master_id, collection_runs.c.start_time)

freshness_sla = Table(
    "freshness_sla",
    metadata,
    Column("id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True),
    Column("master_id", String(50), nullable=False),
    Column("collector_id", String(100), nullable=False),
    Column("sla_hours", Integer, nullable=False),
    Column("last_check_at", DateTime(timezone=True)),
    Column("sla_violated", Integer, server_default="0"),
    UniqueConstraint("master_id", "collector_id"),
)

assets = Table(
    "assets",
    metadata,
    Column("id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True),
    Column("master_id", String(50), nullable=False),
    Column("ext_id", String(200), nullable=False),
    Column("ext_uuid", String(200)),
    Column("name", String(500)),
    Column("type", String(100)),
    Column("os", String(100)),
    Column("payload", JSON),
    Column("collected_at", DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint("master_id", "ext_id"),
)

jobs = Table(
    "jobs",
    metadata,
    Column("id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True),
    Column("master_id", String(50), nullable=False),
    Column("ext_id", String(200), nullable=False),
    Column("job_type", String(100)),
    Column("state", String(50)),
    Column("status_code", Integer),
    Column("policy_name", String(500)),
    Column("policy_type", String(100)),
    Column("asset_ext_uuid", String(200)),
    Column("parent_job_id", String(200)),
    Column("start_time", DateTime(timezone=True)),
    Column("end_time", DateTime(timezone=True)),
    Column("duration_seconds", Integer),
    Column("payload", JSON),
    Column("collected_at", DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint("master_id", "ext_id"),
)

Index("ix_jobs_master_start", jobs.c.master_id, jobs.c.start_time)
Index("ix_jobs_master_status", jobs.c.master_id, jobs.c.status_code)
Index("ix_jobs_collected_at", jobs.c.collected_at)

disk_pools = Table(
    "disk_pools",
    metadata,
    Column("id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True),
    Column("master_id", String(50), nullable=False),
    Column("ext_id", String(200), nullable=False),
    Column("name", String(500)),
    Column("total_capacity_gb", Float),
    Column("used_capacity_gb", Float),
    Column("dedup_ratio", Float),
    Column("storage_category", String(100)),
    Column("payload", JSON),
    Column("collected_at", DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint("master_id", "ext_id"),
)

policies = Table(
    "policies",
    metadata,
    Column("id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True),
    Column("master_id", String(50), nullable=False),
    Column("ext_id", String(200), nullable=False),
    Column("name", String(500)),
    Column("policy_type", String(100)),
    Column("active", Integer, server_default="1"),
    Column("payload", JSON),
    Column("collected_at", DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint("master_id", "ext_id"),
)

job_kpi_daily = Table(
    "job_kpi_daily",
    metadata,
    Column("id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True),
    Column("master_id", String(50), nullable=False),
    Column("day", DateTime(timezone=True), nullable=False),
    Column("total_jobs", Integer, server_default="0"),
    Column("success_jobs", Integer, server_default="0"),
    Column("fail_jobs", Integer, server_default="0"),
    Column("partial_jobs", Integer, server_default="0"),
    Column("avg_duration_seconds", Float),
    Column("p95_duration_seconds", Float),
    Column("built_at", DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint("master_id", "day"),
)

alerts = Table(
    "alerts",
    metadata,
    Column("id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True),
    Column("master_id", String(50)),
    Column("collector_id", String(100)),
    Column("rule", String(100), nullable=False),
    Column("severity", String(20), server_default="warning"),
    Column("message", Text),
    Column("status", String(20), server_default="open"),
    Column("acknowledged_at", DateTime(timezone=True)),
    Column("resolved_at", DateTime(timezone=True)),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

users_table = Table(
    "users",
    metadata,
    Column("id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True),
    Column("username", String(100), nullable=False, unique=True),
    Column("password_hash", String(255), nullable=False),
    Column("role", String(20), server_default="operator"),
    Column("is_active", Integer, server_default="1"),
    Column("last_login_at", DateTime(timezone=True)),
    Column("failed_attempts", Integer, server_default="0"),
    Column("locked_until", DateTime(timezone=True)),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), onupdate=func.now()),
)

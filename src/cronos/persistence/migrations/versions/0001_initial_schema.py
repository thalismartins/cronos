"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-28

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "masters",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("alias", sa.String(200), nullable=False),
        sa.Column("collector_id", sa.String(100), nullable=False),
        sa.Column("family", sa.String(20)),
        sa.Column("state", sa.String(20), server_default="active"),
        sa.Column("freshness_sla_hours", sa.Integer, server_default="8"),
        sa.Column("last_collected_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    op.create_table(
        "collectors",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("enabled", sa.Integer, server_default="1"),
        sa.Column("schedule_cron", sa.String(100)),
        sa.Column("config", postgresql.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "collection_runs",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("collector_id", sa.String(100), nullable=False),
        sa.Column("master_id", sa.String(50), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(20)),
        sa.Column("error_message", sa.Text),
        sa.Column("records_collected", sa.Integer, server_default="0"),
    )
    op.create_index("ix_collection_runs_master_start", "collection_runs", ["master_id", "start_time"])

    op.create_table(
        "freshness_sla",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("master_id", sa.String(50), nullable=False),
        sa.Column("collector_id", sa.String(100), nullable=False),
        sa.Column("sla_hours", sa.Integer, nullable=False),
        sa.Column("last_check_at", sa.DateTime(timezone=True)),
        sa.Column("sla_violated", sa.Integer, server_default="0"),
        sa.UniqueConstraint("master_id", "collector_id"),
    )

    op.create_table(
        "assets",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("master_id", sa.String(50), nullable=False),
        sa.Column("ext_id", sa.String(200), nullable=False),
        sa.Column("ext_uuid", sa.String(200)),
        sa.Column("name", sa.String(500)),
        sa.Column("type", sa.String(100)),
        sa.Column("os", sa.String(100)),
        sa.Column("payload", postgresql.JSON),
        sa.Column("collected_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("master_id", "ext_id"),
    )

    op.create_table(
        "jobs",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("master_id", sa.String(50), nullable=False),
        sa.Column("ext_id", sa.String(200), nullable=False),
        sa.Column("job_type", sa.String(100)),
        sa.Column("state", sa.String(50)),
        sa.Column("status_code", sa.Integer),
        sa.Column("policy_name", sa.String(500)),
        sa.Column("policy_type", sa.String(100)),
        sa.Column("asset_ext_uuid", sa.String(200)),
        sa.Column("parent_job_id", sa.String(200)),
        sa.Column("start_time", sa.DateTime(timezone=True)),
        sa.Column("end_time", sa.DateTime(timezone=True)),
        sa.Column("duration_seconds", sa.Integer),
        sa.Column("payload", postgresql.JSON),
        sa.Column("collected_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("master_id", "ext_id"),
    )
    op.create_index("ix_jobs_master_start", "jobs", ["master_id", "start_time"])
    op.create_index("ix_jobs_master_status", "jobs", ["master_id", "status_code"])
    op.create_index("ix_jobs_collected_at", "jobs", ["collected_at"])

    op.create_table(
        "disk_pools",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("master_id", sa.String(50), nullable=False),
        sa.Column("ext_id", sa.String(200), nullable=False),
        sa.Column("name", sa.String(500)),
        sa.Column("total_capacity_gb", sa.Float),
        sa.Column("used_capacity_gb", sa.Float),
        sa.Column("dedup_ratio", sa.Float),
        sa.Column("storage_category", sa.String(100)),
        sa.Column("payload", postgresql.JSON),
        sa.Column("collected_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("master_id", "ext_id"),
    )

    op.create_table(
        "policies",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("master_id", sa.String(50), nullable=False),
        sa.Column("ext_id", sa.String(200), nullable=False),
        sa.Column("name", sa.String(500)),
        sa.Column("policy_type", sa.String(100)),
        sa.Column("active", sa.Integer, server_default="1"),
        sa.Column("payload", postgresql.JSON),
        sa.Column("collected_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("master_id", "ext_id"),
    )

    op.create_table(
        "job_kpi_daily",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("master_id", sa.String(50), nullable=False),
        sa.Column("day", sa.DateTime(timezone=True), nullable=False),
        sa.Column("total_jobs", sa.Integer, server_default="0"),
        sa.Column("success_jobs", sa.Integer, server_default="0"),
        sa.Column("fail_jobs", sa.Integer, server_default="0"),
        sa.Column("partial_jobs", sa.Integer, server_default="0"),
        sa.Column("avg_duration_seconds", sa.Float),
        sa.Column("p95_duration_seconds", sa.Float),
        sa.Column("built_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("master_id", "day"),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("master_id", sa.String(50)),
        sa.Column("collector_id", sa.String(100)),
        sa.Column("rule", sa.String(100), nullable=False),
        sa.Column("severity", sa.String(20), server_default="warning"),
        sa.Column("message", sa.Text),
        sa.Column("status", sa.String(20), server_default="open"),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True)),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("alerts")
    op.drop_table("job_kpi_daily")
    op.drop_table("policies")
    op.drop_table("disk_pools")
    op.drop_index("ix_jobs_collected_at")
    op.drop_index("ix_jobs_master_status")
    op.drop_index("ix_jobs_master_start")
    op.drop_table("jobs")
    op.drop_table("assets")
    op.drop_table("freshness_sla")
    op.drop_index("ix_collection_runs_master_start")
    op.drop_table("collection_runs")
    op.drop_table("collectors")
    op.drop_table("masters")

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import Engine, func, select, text

from cronos.persistence.schema import collection_runs, masters


def evaluate_alerts(engine: Engine) -> list[dict]:
    results = []
    with engine.begin() as conn:
        masters_list = conn.execute(select(masters)).mappings().fetchall()

        for m in masters_list:
            mid = m["id"]
            sla_hours = m.get("freshness_sla_hours") or 8

            last_run = conn.execute(
                select(collection_runs.c.start_time)
                .where(collection_runs.c.master_id == mid)
                .order_by(collection_runs.c.start_time.desc())
                .limit(1)
            ).scalar()

            if last_run:
                lag = (datetime.now(UTC) - last_run).total_seconds() / 3600
                if lag > sla_hours:
                    rule = "freshness_sla"
                    msg = f"Master {mid} last collected {lag:.1f}h ago (SLA: {sla_hours}h)"
                    conn.execute(
                        text("""
                            INSERT INTO alerts (master_id, rule, severity, message, status, created_at)
                            VALUES (:mid, :rule, 'warning', :msg, 'open', :now)
                            ON CONFLICT DO NOTHING
                        """),
                        {"mid": mid, "rule": rule, "msg": msg, "now": datetime.now(UTC)},
                    )
                    results.append({"master_id": mid, "rule": rule, "message": msg})

            recent_fails = conn.execute(
                select(func.count()).select_from(collection_runs)
                .where(
                    collection_runs.c.master_id == mid,
                    collection_runs.c.status == "failed",
                    collection_runs.c.start_time >= datetime.now(UTC) - timedelta(hours=24),
                )
            ).scalar() or 0

            if recent_fails >= 3:
                rule = "collection_failures"
                msg = f"Master {mid} has {recent_fails} failed collections in 24h"
                conn.execute(
                    text("""
                        INSERT INTO alerts (master_id, rule, severity, message, status, created_at)
                        VALUES (:mid, :rule, 'critical', :msg, 'open', :now)
                        ON CONFLICT DO NOTHING
                    """),
                    {"mid": mid, "rule": rule, "msg": msg, "now": datetime.now(UTC)},
                )
                results.append({"master_id": mid, "rule": rule, "message": msg})

    return results

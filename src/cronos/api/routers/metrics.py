from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from sqlalchemy import text

from cronos.persistence.db import get_readonly_engine

router = APIRouter()


@router.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    engine = get_readonly_engine()
    with engine.connect() as conn:
        total_jobs = conn.execute(text("SELECT COUNT(*) FROM jobs")).scalar() or 0
        total_assets = conn.execute(text("SELECT COUNT(*) FROM assets")).scalar() or 0
        total_masters = conn.execute(text("SELECT COUNT(*) FROM masters")).scalar() or 0
        failed_runs = conn.execute(
            text("SELECT COUNT(*) FROM collection_runs WHERE status = 'failed'")
        ).scalar() or 0

    return PlainTextContent(f"""# HELP cronos_jobs_total Total jobs collected
# TYPE cronos_jobs_total gauge
cronos_jobs_total {total_jobs}
# HELP cronos_assets_total Total assets tracked
# TYPE cronos_assets_total gauge
cronos_assets_total {total_assets}
# HELP cronos_masters_total Total masters configured
# TYPE cronos_masters_total gauge
cronos_masters_total {total_masters}
# HELP cronos_collection_failed_runs Total failed collection runs
# TYPE cronos_collection_failed_runs gauge
cronos_collection_failed_runs {failed_runs}
""")


class PlainTextContent(PlainTextResponse):
    media_type = "text/plain; version=0.0.4"

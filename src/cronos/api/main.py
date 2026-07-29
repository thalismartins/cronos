from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from cronos.api.routers import (
    alerts_router,
    assets,
    auth,
    collection,
    collection_runs,
    health,
    infra,
    jobs_router,
    kpis,
    masters,
    metrics,
    resilience,
    security_router,
    storage_router,
)

app = FastAPI(
    title="Cronos API",
    version="0.1.0",
    description="Data resilience collection and observability platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(kpis.router, prefix="/api/v1", tags=["kpis"])
app.include_router(jobs_router.router, prefix="/api/v1", tags=["jobs"])
app.include_router(masters.router, prefix="/api/v1", tags=["masters"])
app.include_router(assets.router, prefix="/api/v1", tags=["assets"])
app.include_router(collection.router, prefix="/api/v1", tags=["collection"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(collection_runs.router, prefix="/api/v1", tags=["collection"])
app.include_router(metrics.router, tags=["metrics"])
app.include_router(storage_router.router, prefix="/api/v1", tags=["storage"])
app.include_router(resilience.router, prefix="/api/v1", tags=["resilience"])
app.include_router(security_router.router, prefix="/api/v1", tags=["security"])
app.include_router(infra.router, prefix="/api/v1", tags=["infrastructure"])
app.include_router(alerts_router.router, prefix="/api/v1", tags=["alerts"])

_dist = Path(__file__).parents[3] / "web" / "dist"
if _dist.exists():
    app.mount("/", StaticFiles(directory=str(_dist), html=True), name="frontend")

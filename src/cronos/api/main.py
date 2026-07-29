from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cronos.api.routers import (
    assets,
    auth,
    collection,
    collection_runs,
    health,
    jobs,
    kpis,
    masters,
    metrics,
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
app.include_router(jobs.router, prefix="/api/v1", tags=["jobs"])
app.include_router(masters.router, prefix="/api/v1", tags=["masters"])
app.include_router(assets.router, prefix="/api/v1", tags=["assets"])
app.include_router(collection.router, prefix="/api/v1", tags=["collection"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(collection_runs.router, prefix="/api/v1", tags=["collection"])
app.include_router(metrics.router, tags=["metrics"])


@app.get("/")
async def root():
    return {"name": "Cronos", "version": "0.1.0"}

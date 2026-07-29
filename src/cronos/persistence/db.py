from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy import event as sa_event

from cronos.config import settings

_engine: Engine | None = None
_readonly_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = _build_engine()
    return _engine


def get_readonly_engine() -> Engine:
    global _readonly_engine
    if _readonly_engine is None:
        url = str(settings.cronos_db_path)
        ro_url = url.replace("postgresql+psycopg://", "postgresql+psycopg://")
        _readonly_engine = _build_engine(ro_url)
    return _readonly_engine


def _build_engine(url: str | None = None) -> Engine:
    target = url or settings.cronos_db_path

    e = create_engine(
        target,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )

    @sa_event.listens_for(e, "connect")
    def _set_utc(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("SET TIME ZONE 'UTC'")
        cursor.close()

    return e


def dispose_engines() -> None:
    global _engine, _readonly_engine
    if _engine:
        _engine.dispose()
        _engine = None
    if _readonly_engine:
        _readonly_engine.dispose()
        _readonly_engine = None

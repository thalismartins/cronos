from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cronos_db_path: str = "postgresql+psycopg://cronos:cronos@127.0.0.1:5432/cronos"
    cronos_auth_secret: str = ""
    cronos_redis_url: str = ""
    cronos_log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()


def load_collectors_config(path: Path | None = None) -> dict[str, Any]:
    if path is None:
        path = Path("config/collectors.yaml")
    if not path.exists():
        return {"collectors": []}
    with open(path) as f:
        return yaml.safe_load(f) or {}

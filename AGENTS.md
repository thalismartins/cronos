# Agent Guide — Cronos

This is the single source of truth for every AI coding agent working in this repo.

## Hard rules
1. No sensitive data ever.
2. Secrets only via environment variables.
3. Examples use placeholders only.

## Stack
- Backend: Python 3.12+, httpx (async), SQLAlchemy 2.0 Core, Alembic, FastAPI, pytest.
- Frontend: Vite + Preact + TypeScript + uPlot.
- DB: PostgreSQL (psycopg 3).

## Tests
```bash
uv sync --extra dev
uv run ruff check src tests
uv run mypy src
uv run pytest tests/
```

## Workflow
- Never commit to main. One branch per task.
- Definition of Done: CI green, migrations + tests + docs updated.

# Deployment

## Docker (Recommended)

```bash
docker compose up -d
```

## Manual

```bash
# Prerequisites: PostgreSQL 17+, Python 3.12+, uv
cp .env.example .env
# Edit .env with DB connection

uv sync
cronos-migrate
cronos-seed-demo    # Optional: populate demo data
cronos-serve        # API on :8000
cronos-scheduler    # Background collection scheduler
```

## Environment Variables
- `CRONOS_DB_PATH` — PostgreSQL DSN
- `CRONOS_AUTH_SECRET` — JWT signing key (min 32 chars)
- `CRONOS_REDIS_URL` — Optional Redis for cache
- `CRONOS_LOG_LEVEL` — DEBUG, INFO, WARN, ERROR

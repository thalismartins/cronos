FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

FROM python:3.12-slim AS web-builder
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci && npm run build

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv .venv
COPY --from=builder /app/src src
COPY --from=web-builder /web/dist web/dist
COPY alembic.ini .

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import http.client; http.client.HTTPConnection('localhost',8000).request('GET','/health'); exit(0)"

ENTRYPOINT ["cronos-serve"]

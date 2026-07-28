## Descricao

Implementar API FastAPI com endpoints KPI.

- [ ] src/cronos/api/main.py: app FastAPI, middleware (CORS, request ID, logging)
- [ ] src/cronos/api/routers/: kpis.py, jobs.py, assets.py, masters.py, collection.py
- [ ] src/cronos/api/schemas.py: Pydantic schemas por endpoint
- [ ] src/cronos/api/deps.py: dependencias (DB session readonly, paginacao, filtros)
- [ ] Paginacao keyset (cursor-based)
- [ ] Filtros: master, window (24h/7d/30d), status, job_type

**Endpoints:**
- GET /api/v1/kpis/performance
- GET /api/v1/kpis/operations
- GET /api/v1/kpis/storage
- GET /api/v1/kpis/resilience
- GET /api/v1/jobs
- GET /api/v1/jobs/summary
- GET /api/v1/assets
- GET /api/v1/masters (com freshness)
- GET /api/v1/collection-runs

## Definicao de Done
- [ ] Todos os endpoints retornam dados corretos com dados demo
- [ ] Paginacao keyset funcional
- [ ] Filtros combinaveis
- [ ] Testes de API com httpx + respx

## Referencia
- [SPEC.md](SPEC.md) secao 8 (API)

## Descricao

Adicionar metricas Prometheus para observabilidade operacional.

- [ ] Endpoint /metrics no formato OpenMetrics
- [ ] Metricas do scheduler: cronos_collect_duration_seconds, cronos_collect_freshness_seconds, cronos_collect_total
- [ ] Metricas da API: request duration, status codes, active users
- [ ] Metricas do banco: connection pool size, active queries
- [ ] Health check: /health (liveness) e /ready (readiness + DB ping)

## Definicao de Done
- [ ] /metrics retorna metricas validas (curl | promtool check metrics)
- [ ] /health retorna 200
- [ ] /ready retorna 200 so quando DB responde
- [ ] Nao expoe dados sensveis nas metricas

## Referencia
- [SPEC.md](SPEC.md) secao 9.2 (Metricas do Scheduler)

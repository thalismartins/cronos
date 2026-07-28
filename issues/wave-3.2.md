## Descricao

Adicionar cache layer e transacoes read-only para performance.

- [ ] cachetools.TTLCache para respostas de KPI (TTL 60s, configuravel)
- [ ] Cache invalidado quando collector escreve novos dados
- [ ] Redis opcional (fallback para memoria local)
- [ ] Todas as queries de KPI usam postgresql_readonly
- [ ] Header Cache-Control nas respostas

## Definicao de Done
- [ ] Mesma request em 2 segundos retorna cached (nao vai ao DB)
- [ ] Apos coleta, cache daquele master e invalidado
- [ ] Sem Redis funcionando, usa cache em memoria
- [ ] Redis configurado via DRND_REDIS_URL

## Referencia
- [SPEC.md](SPEC.md) secao 8.3 (Cache)

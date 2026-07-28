## Descricao

Implementar particionamento automatico e prunning de dados.

**Particionamento:**
- [ ] Migration Alembic que cria tabelas particionadas por RANGE (collected_at)
- [ ] Comando cronos-partition-create para criar particoes futuras (N meses)
- [ ] Particionamento CONCURRENTLY para tabelas existentes

**Rollups:**
- [ ] cronos-rollup: constroi tabelas job_kpi_daily, storage_snapshot_daily
- [ ] Query de KPI usa rollup com fallback para tabela raw
- [ ] Rollup incremental (apenas dados desde o ultimo rollup)

**Prunning:**
- [ ] cronos-prune: apaga dados brutos e rollups fora da janela de retencao
- [ ] Retencao configuravel por tabela (collectors.yaml)
- [ ] Dry-run mode (--dry-run)

## Definicao de Done
- [ ] Tabela jobs com 3 particoes mensais criadas
- [ ] Rollup cobre 100% das queries de KPI
- [ ] Prune remove dados antigos sem quebrar queries
- [ ] Testes de performance com 1M+ linhas

## Referencia
- [SPEC.md](SPEC.md) secao 6 (Database Optimization)

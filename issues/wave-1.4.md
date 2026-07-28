## Descricao

Implementar coletor de demonstracao (dados sinteticos) e scheduler CRON.

**Coletor Demo:**
- [ ] collectors/demo/plugin.py: gera dados sinteticos (jobs, storage, assets)
- [ ] Modo standalone: cronos-seed-demo populando o banco
- [ ] Configuravel: numero de masters, jobs, janela de tempo

**Scheduler:**
- [ ] src/cronos/scheduler/: engine que le CRON de cada coletor em collectors.yaml
- [ ] Dispara coleta no horario, com fila por master
- [ ] Retry com backoff exponencial (max 3 tentativas)
- [ ] Registra collection_runs (start, end, status, error)

## Definicao de Done
- [ ] cronos-seed-demo gera dados e persiste no PostgreSQL
- [ ] Scheduler dispara coletor demo no CRON configurado
- [ ] Falha parcial (um master) nao afeta outros
- [ ] Logs sem tokens/hosts/payloads

## Referencia
- [SPEC.md](SPEC.md) secoes 5 (Scheduler) e 9 (Daily Collection)

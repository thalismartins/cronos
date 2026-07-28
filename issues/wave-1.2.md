## Descricao

Implementar a camada de persistencia:

- [ ] src/cronos/persistence/db.py: engines PostgreSQL (UTC, readonly via postgresql_readonly)
- [ ] src/cronos/persistence/schema.py: tabelas base (masters, collectors, collection_runs, freshness_sla)
- [ ] alembic.ini + migrations iniciais
- [ ] src/cronos/persistence/repositories.py: upsert idempotente, queries base
- [ ] Indices KPI-orientados ((master_id, collected_at), etc.)

## Definicao de Done
- [ ] Migration cria schema sem erro
- [ ] cronos-migrate executa todas as migracoes
- [ ] Rollback funcional (alembic downgrade -1)
- [ ] Testes de repositorio com PostgreSQL real

## Referencia
- [SPEC.md](SPEC.md) secoes 6 (DB Optimization) e 7 (Data Model)

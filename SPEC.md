# Cronos — Spec do Projeto

> **Inspiração:** Data-Resilience-NBU-OPS
> **Propósito:** Plataforma genérica de coleta programável, dashboard de
> resiliência e observabilidade, com otimização de banco de dados nativa.
> **Licença:** MIT

---

## 1. Filosofia

Cronos resolve o que o DRND faz bem (coletar, armazenar, visualizar KPIs de
resiliência) mas generaliza para **qualquer fonte de dados** e torna a
**coleta programável** por design. Onde o DRND é amarrado à API REST da
NetBackup e a um schema fixo de jobs/policies/assets, o Cronos expõe:

1. Um **sistema de plugins** para coletores (qualquer fonte: REST API, banco,
   SNMP, arquivo, cloud).
2. Um **scheduler interno** com expressões CRON por coletor, com SLA de
   frescor, retry com backoff e alerta por atraso.
3. **Otimização de banco nativa**: particionamento automático por tempo,
   rollups configuráveis, prunning por retenção, sem intervenção DBA.

---

## 2. Stack

| Camada | Tecnologia |
|---|---|
| Runtime | Python 3.12+ (uv) |
| Web framework | FastAPI |
| ORM | SQLAlchemy 2.0 Core |
| Migrations | Alembic |
| DB | PostgreSQL 17+ (psycopg 3) |
| Scheduler | APScheduler ou scheduler interno |
| Frontend | Vite + Preact + TypeScript + uPlot |
| Auth | JWT (HS256) + Argon2id |
| LDAP/AD | ldap3 (opcional) |
| Metrics | Prometheus /openmetrics |
| Cache | cachetools + Redis opcional |
| Container | Docker + docker-compose (dev) |

---

## 3. Arquitetura

```
┌─────────────────────────────────────────────────────┐
│                    Web UI                            │
│            (Vite + Preact + uPlot)                   │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP (/api/v1)
┌──────────────────────▼──────────────────────────────┐
│               FastAPI (read-mostly)                   │
│    Cache layer │ Auth (JWT) │ Rate Limit │ CORS      │
└──────┬──────────────────────────────────┬────────────┘
       │ read                             │ write
┌──────▼──────────────────────────────────▼────────────┐
│              PostgreSQL (particionado)                 │
│   Rollups diários │ Prunning │ Views materializadas   │
└──────────────────────────────────────────────────────┘
       ▲ write (collection_run)
┌──────┴────────────────────────────────────────────────┐
│              Collector Pipeline                        │
│  Validation → Transform → Idempotent Upsert → Append  │
└──────────────────────────────────────────────────────┘
       ▲ schedule / trigger
┌──────┴────────────────────────────────────────────────┐
│           Scheduler (CRON + gatilho manual)            │
│   Freshness SLA │ Retry │ Backoff │ Alerta por atraso │
└──────────────────────────────────────────────────────┘
       ▲ plugin discovery
┌──────┴────────────────────────────────────────────────┐
│         Coletores Programáveis (plugins)               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ NetBackup │ │  Veeam   │ │  Custom  │ │   SNMP   │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
└──────────────────────────────────────────────────────┘
```

---

## 4. Sistema de Plugins (Coletores Programáveis)

### 4.1 Interface do Coletor

Cada coletor é um módulo Python que implementa a interface:

```python
class Collector(ABC):
    """Interface base que todo coletor deve implementar."""

    @property
    def id(self) -> str: ...
    def config_schema(self) -> dict: ...
    def capabilities(self) -> list[str]: ...
    def validate_config(self, config: dict) -> bool: ...

    async def collect(
        self, config: dict, state: CollectorState
    ) -> AsyncGenerator[Record, None]: ...
```

### 4.2 Descoberta

Coletores são descobertos em `collectors/` ou instalados via pip como
`cronos-collector-*`. Cada plugin declara:
- `id`: identificador único (ex: `netbackup`, `veeam`, `custom-sql`)
- `config_schema`: JSON Schema para validação da configuração
- `capabilities`: lista de capacidades (ex: `jobs`, `storage`, `inventory`)

### 4.3 Registro

```yaml
# config/collectors.yaml
collectors:
  - id: netbackup
    enabled: true
    schedule: "0 */6 * * *"
    freshness_sla: 8h
    retry:
      max_attempts: 3
      backoff: exponential
    config:
      masters:
        - alias: prod-bu
          base_url: https://nbu-prod.example.com
          api_key_env: NBUPROD_API_KEY
          family: "11.x"
```

---

## 5. Scheduler & Rotinas de Coleta

### 5.1 CRON por Coletor

Cada coletor tem sua própria expressão CRON. O scheduler:

- Dispara a coleta no horário agendado
- Mantém fila por master/tenant
- Monitora **frescor** (timestamp do último dado coletado)
- Aplica **retry** com backoff exponencial em falha
- Aciona **alerta** se frescor exceder `freshness_sla`

### 5.2 Coleta Diária (Rotina)

Tabelas de snapshot recebem uma coleta full a cada execução. Tabelas de
evento (jobs, logs) usam **incremental baseado em checkpoint**:

```
last_checkpoint = redis.get(f"checkpoint:{collector_id}:{master_id}")
# ou fallback: DB (collection_runs.ended_at)
collect(from = last_checkpoint, to = now)
```

### 5.3 Transações por Master

Cada `collection_run` é uma transação isolada por master. Falha em um master
não afeta os outros. O partial-failure é reportado no collection_run.

---

## 6. Otimização de Banco de Dados

### 6.1 Particionamento Automático

Tabelas de evento (`jobs`, `snapshots`, `logs`) são particionadas por
intervalo de tempo automaticamente via migration Alembic:

```sql
CREATE TABLE jobs (
    id BIGSERIAL,
    master_id VARCHAR(50),
    collected_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ...
) PARTITION BY RANGE (collected_at);
```

Partições mensais são criadas com N meses de antecedência pelo CLI.

### 6.2 Rollups Diários

Para cada tabela de evento, uma tabela de rollup diário é mantida:

```
jobs → job_kpi_daily (success, fail, partial por master/dia)
storage → storage_snapshot_daily (capacity, dedup por pool/dia)
```

Rollups são construídos pelo comando `cronos-rollup` (out-of-band).

### 6.3 Prunning Automático

Retenção configurável por coletor:

```yaml
retention:
  raw_jobs: 90d
  rollups: 365d
  snapshots: 30d
```

### 6.4 Índices KPI-Orientados

Índices compostos por consulta de KPI:
- `(master_id, collected_at)` para janelas de tempo
- `(master_id, status, collected_at)` para contagem por status
- Criação com CONCURRENTLY em produção (sem lock)

### 6.5 Transações Read-Only

Todas as queries de KPI usam `postgresql_readonly`. Apenas coletores e
scheduler escrevem.

---

## 7. Data Model

### 7.1 Metadata

| Tabela | Descrição | Tipo |
|---|---|---|
| `masters` | Fontes de dados | Current state |
| `collectors` | Plugins registrados + config | Reference |
| `collection_runs` | Histórico de execuções | Event |
| `freshness_sla` | SLA de frescor por master | Reference |

### 7.2 Dados de Coleta (dinâmicos)

Cada coletor declara seu schema. Tabelas base:

**Current state** (upsert por natural key):
- `assets`, `policies`, `storage_units`, `disk_pools`, `media`
- Natural key: `UNIQUE(master_id, ext_id)`

**Event** (append, particionadas):
- `jobs`, `alerts`, `logs`, `malware_scans`, `recovery_points`

**Snapshot** (append, particionadas):
- `disk_pool_snapshots`, `node_snapshots`, `slp_backlog`

### 7.3 Schema Dinâmico

Coletores podem estender o schema via campos JSONB para dados
específicos do vendor.

---

## 8. API

### 8.1 Padrão

- Versionada (`/api/v1`)
- Read-only para dados (writes: auth + feedback)
- Pydantic schemas separados das tabelas
- Paginação keyset
- Filtros por `?master=`, `?window=24h|7d|30d`, `?status=`
- CORS configurável por origin

### 8.2 Endpoints Principais

```
GET  /api/v1/kpis/performance
GET  /api/v1/kpis/operations
GET  /api/v1/kpis/storage
GET  /api/v1/kpis/resilience
GET  /api/v1/jobs
GET  /api/v1/jobs/summary
GET  /api/v1/assets
GET  /api/v1/masters
GET  /api/v1/collection-runs
POST /api/v1/collect
POST /api/v1/collect/{master_id}
```

### 8.3 Cache

Respostas de KPI cacheadas por TTL (default 60s) via `cachetools`.
Redis opcional para multi-instância.

---

## 9. Coleta Diária Automatizada

### 9.1 Rotina Diária (exemplo)

```
00:01 — NetBackup collector (jobs incrementais)
00:05 — Assets, policies, storage (full)
00:10 — Snapshots de disk_pools
00:20 — Rollup diário (cronos-rollup)
```

### 9.2 Métricas do Scheduler

```
cronos_collect_duration_seconds{collector, master, status}
cronos_collect_freshness_seconds{collector, master}
cronos_collect_total{collector, status}
```

### 9.3 Execução Manual

`POST /api/v1/collect/{master_id}` — gatilho manual pelo dashboard.

---

## 10. Plano de Implementação (Waves)

### Wave 1 — Fundação (Semanas 1-2)
- Estrutura do projeto, pyproject.toml, CLI entrypoints
- PostgreSQL engine + Alembic + schema base
- Plugin system: interface Collector, descoberta, validação
- Coletor de exemplo (demo)
- Scheduler básico (CRON por coletor)

### Wave 2 — Coletores & Dados (Semanas 3-4)
- Coletor NetBackup (portado do DRND)
- Coletor Veeam (exemplo de segundo vendor)
- Pipeline de transformação/normalização
- Particionamento automático + prunning

### Wave 3 — API & Cache (Semanas 5-6)
- FastAPI + endpoints KPI
- Cache layer + readonly transactions
- Auth (JWT + Argon2id + LDAP opcional)
- Rate limiting

### Wave 4 — Web UI (Semanas 7-8)
- Vite + Preact + TypeScript
- Design system premium (CSS variables, glassmorphism)
- Dashboard de KPIs
- Página de coletores (status, freshness, run history)
- Trigger manual de coleta

### Wave 5 — Enterprise (Semanas 9-10)
- Prometheus metrics
- Rollups diários + prunning
- Freshness SLA + alertas
- Docker + docker-compose
- Docs: SECURITY, THREAT_MODEL, ADRs
- CI/CD: ruff, mypy, pytest, frontend build
- Testes E2E (Playwright)
- SEO/a11y audit

---

## 11. Melhorias em Relação ao DRND

| Aspecto | DRND | Cronos |
|---|---|---|
| Coletores | Apenas NetBackup | Plugin-based, qualquer fonte |
| Schedule | Scheduler fixo interno | CRON por coletor |
| Particionamento | Manual/DBA | Automático (CONCURRENTLY) |
| Rollups | Build manual | Automático + agendado |
| Cache | Nenhum | cachetools + Redis opcional |
| Freshness SLA | Não tem | Monitorado e alertável |
| Rate limit | Nenhum | Configurável por rota |
| Docker | Não | docker-compose para dev |
| Frontend tests | Zero | Planejado |
| E2E tests | Zero | Playwright |
| Multi-tenant | Apenas masters | Masters + tenants |
| Schema dinâmico | Fixo | JSONB extensions |
| Config | JSON + env vars | YAML + env vars |

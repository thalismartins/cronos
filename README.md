# Cronos

Plataforma genérica de coleta programável, dashboard de resiliência e
observabilidade com otimização de banco de dados nativa.

## Quick start

```bash
git clone https://github.com/thalismartins/cronos.git
cd cronos
cp .env.example .env
# edit .env with your PostgreSQL connection

uv sync
cronos-migrate
cronos-seed-demo
cronos-serve
```

## Docs

- [SPEC.md](SPEC.md) — spec completa do projeto
- `docs/` — documentação detalhada (em construção)

## License

MIT

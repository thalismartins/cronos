## Descricao

Criar a estrutura base do projeto Cronos:

- [ ] pyproject.toml com dependencias (FastAPI, SQLAlchemy, Alembic, httpx, etc.)
- [ ] src/cronos/ pacote principal
- [ ] Entrypoints CLI: cronos-collect, cronos-serve, cronos-migrate, cronos-seed-demo, cronos-rollup, cronos-prune
- [ ] AGENTS.md + CONTRIBUTING.md para agentes multi-AI
- [ ] .env.example + config/collectors.yaml.example
- [ ] .gitignore, ruff.toml, mypy.ini

## Definicao de Done
- [ ] uv sync --extra dev instala sem erro
- [ ] cronos --help lista todos os comandos
- [ ] ruff + mypy passam
- [ ] README.md com visao geral e quick start

## Referencia
- [SPEC.md](SPEC.md) secoes 2 (Stack) e 10 (Wave 1)

## Descricao

Dockerizar o projeto para desenvolvimento e producao.

- [ ] Dockerfile multi-stage (builder + runtime)
- [ ] docker-compose.yml: api + db + redis + scheduler
- [ ] Entrypoint que roda migrate antes de serve
- [ ] .dockerignore otimizado
- [ ] Healthcheck no Dockerfile
- [ ] Documentacao de deploy com docker

## Definicao de Done
- [ ] docker compose up --build inicia tudo sem erro
- [ ] API responde em localhost:8000
- [ ] Scheduler roda como processo separado
- [ ] Dados persistem entre restarts (volume)

## Referencia
- [SPEC.md](SPEC.md) secao 2 (Stack - Container)

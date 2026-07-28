## Descricao

Portar o coletor NetBackup do projeto DRND para o Cronos como plugin.

- [ ] collectors/netbackup/plugin.py: implementa interface Collector
- [ ] collectors/netbackup/client.py: httpx async, auth header, paginacao, retry, safe logging
- [ ] collectors/netbackup/versioning.py: deteccao de versao 10.x/11.x, adapter por familia
- [ ] Capacidades: jobs, policies, assets, storage, media, SLP, catalog, malware, appliances
- [ ] collectors/netbackup/config_schema.py: JSON Schema para configuracao YAML

## Definicao de Done
- [ ] cronos-collect --id netbackup executa coleta completa
- [ ] Dados normalizados para o schema base (jobs, assets, storage)
- [ ] Retry respeita Retry-After, backoff, max 4 tentativas
- [ ] Log sem tokens, hostnames ou payloads
- [ ] Testes com respx (mock da API NetBackup)

## Referencia
- [SPEC.md](SPEC.md) secoes 4.3 (Registro) e 11 (Melhorias)

## Descricao

Criar o sistema de plugins que permite coletores programaveis:

- [ ] src/cronos/collector/interface.py: classe abstrata Collector com metodos collect(), config_schema(), capabilities(), validate_config()
- [ ] src/cronos/collector/discovery.py: descoberta automatica de coletores em collectors/ e via entrypoints pip
- [ ] src/cronos/collector/registry.py: registro central de coletores disponiveis
- [ ] Record schema: tipo generico de saida do coletor (categoria + payload JSONB + metadata)
- [ ] Testes unitarios com coletor mock

## Definicao de Done
- [ ] Coletor mock registra e executa via cronos-collect --id mock
- [ ] config_schema() retorna JSON Schema valido
- [ ] validate_config() rejeita config invalida
- [ ] Descoberta encontra coletores em collectors/

## Referencia
- [SPEC.md](SPEC.md) secao 4 (Plugin System)

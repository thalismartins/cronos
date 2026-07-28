## Descricao

Criar pipeline de transformacao e normalizacao entre coletores e o banco.

- [ ] src/cronos/pipeline/validator.py: validacao de registros contra schema
- [ ] src/cronos/pipeline/transformer.py: normalizacao de campos (timestamps, enums, IDs)
- [ ] src/cronos/pipeline/router.py: direciona cada Record para a tabela correta
- [ ] Suporte a campos JSONB para dados especificos de vendor
- [ ] Schema dinamico: tabelas de evento com payload JSONB

## Definicao de Done
- [ ] Pipeline valida schema antes de persistir
- [ ] Registros invalidos sao logados e ignorados (nao quebram a coleta)
- [ ] JSONB permite extensao sem migration
- [ ] Testes com dados malformados

## Referencia
- [SPEC.md](SPEC.md) secoes 7.3 (Schema Dinamico) e 3 (Pipeline)

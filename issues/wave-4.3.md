## Descricao

Pagina de gerenciamento de coletores e gatilho manual.

- [ ] Pagina Collectors: lista de coletores registrados com status (idle/running/failed)
- [ ] Indicador de freshness: ha quanto tempo o ultimo collect rodou
- [ ] Botao Start Collect por master + Collect All
- [ ] Historico de collection_runs (tabela com start, end, status, error)
- [ ] Botao de agendamento: editar CRON expression no UI
- [ ] Indicador de SLA violado (freshness > freshness_sla)

## Definicao de Done
- [ ] Trigger manual POST /api/v1/collect/{master_id} funciona
- [ ] Status do coletor atualiza em tempo real (polling)
- [ ] Historico mostra ultimas N execucoes
- [ ] SLA violado aparece em vermelho com tooltip

## Referencia
- [SPEC.md](SPEC.md) secoes 5.1 (CRON) e 9.3 (Execucao Manual)

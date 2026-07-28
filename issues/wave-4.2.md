## Descricao

Construir o dashboard de KPIs com graficos e tabelas.

**Componentes:**
- [ ] App shell: sidebar (navegacao com icones) + topbar (brand, master selector, theme toggle, last-updated)
- [ ] Overview: KPI stat cards (total jobs, success, fail, partial) com tendencia + window selector
- [ ] Jobs page: tabela premium com sorting, filtros, paginacao keyset, sticky header
- [ ] Top Status Codes: cards com severidade, ocorrencias, acao sugerida
- [ ] Storage: capacidade/dedup com uPlot estilizado com tokens
- [ ] Resilience: recovery points, malware scans, airgap status
- [ ] Topology: appliances, clusters, nodes com status dots (visual, nao lista)

**Graficos uPlot:**
- [ ] Tematizado com CSS variables (axis, grid, series)
- [ ] Tabular nums nos tooltips
- [ ] Re-theme ao trocar dark/light

## Definicao de Done
- [ ] Todos os componentes renderizam com dados demo
- [ ] uPlot reflete as cores do tema ativo
- [ ] Navegacao entre paginas via hash routing
- [ ] Auto-refresh respeita intervalo configurado
- [ ] Testes com Preact Testing Library

## Referencia
- [SPEC.md](SPEC.md) secao 10 (Wave 4)

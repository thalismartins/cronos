## Descricao

Sistema de alertas baseado em freshness SLA e outras condicoes.

- [ ] Engine de regras: freshness SLA violado, coleta falhou N vezes seguidas, DB disk space baixo
- [ ] Notificacoes: webhook (Slack/Teams), email (SMTP configuravel)
- [ ] Pagina de alertas no dashboard (historico, status, acknowledge)
- [ ] Configuracao via YAML (alertas por coletor, thresholds)

## Definicao de Done
- [ ] Coleta parada por X horas dispara alerta
- [ ] Webhook POST para Slack funciona
- [ ] Alerta resolvido quando coleta retoma
- [ ] Historico de alertas visivel no dashboard

## Referencia
- [SPEC.md](SPEC.md) secao 5.1 (Freshness SLA)

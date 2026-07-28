## Descricao

Testes end-to-end com Playwright.

- [ ] Playwright configurado (chromium + firefox)
- [ ] Teste: login com credenciais validas
- [ ] Teste: login com credenciais invalidas (deve bloquear)
- [ ] Teste: overview carrega KPIs corretamente
- [ ] Teste: navegacao entre todas as paginas
- [ ] Teste: dark/light toggle persiste
- [ ] Teste: trigger manual de coleta
- [ ] Teste: responsividade (mobile 375px, tablet 768px, desktop 1280px)

## Definicao de Done
- [ ] npx playwright test --all passa
- [ ] Testes rodam em CI (com PostgreSQL service + demo data)
- [ ] Screenshots de referencia para comparacao visual
- [ ] Cobertura minima: 3 fluxos criticos (login, overview, coleta)

## Referencia
- [SPEC.md](SPEC.md) secao 10 (Wave 5 - Testes E2E)

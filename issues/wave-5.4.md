## Descricao

Documentacao de seguranca, threat model, ADRs e CI/CD.

**Docs:**
- [ ] SECURITY.md: politica de divulgacao, chaves, contato
- [ ] THREAT_MODEL.md: modelo de ameacas (STRIDE por componente)
- [ ] ADRs: decisoes arquiteturais (particionamento, scheduler, plugin system)
- [ ] CAPACITY.md: dimensionamento (jobs/dia, masters, retencao)
- [ ] DEPLOY.md: deploy manual + docker + systemd
- [ ] RELEASE.md: fluxo de release, versionamento semantico

**CI/CD:**
- [ ] GitHub Actions: ruff check, mypy, pytest (PostgreSQL service), frontend build
- [ ] Dependabot: pip + npm
- [ ] SBOM (CycloneDX) nos releases
- [ ] SHA-256 checksums nos artifacts

## Definicao de Done
- [ ] CI passa em todos os checks
- [ ] Dependabot cria PRs automaticamente
- [ ] Release .zip com checksum + SBOM
- [ ] ADRs aprovados e mergeados

## Referencia
- [SPEC.md](SPEC.md) secao 10 (Wave 5)

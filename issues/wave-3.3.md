## Descricao

Implementar autenticacao e autorizacao.

- [ ] JWT (HS256) + Argon2id para hash de senha
- [ ] POST /api/v1/auth/login (unica rota publica)
- [ ] Bearer token obrigatorio em /api/v1/*
- [ ] RBAC: admin / operator / auditor
- [ ] Rate limiting no login (por IP, N tentativas/minuto)
- [ ] Block temporario apos N falhas consecutivas
- [ ] LDAP/AD opcional (ldap3)

## Definicao de Done
- [ ] Login retorna JWT valido
- [ ] Rota sem token retorna 401
- [ ] Rate limit bloqueia apos N tentativas
- [ ] Admin ve tudo, operator nao ve security/audit
- [ ] Testes de auth (token invalido, expirado, role errada)

## Referencia
- [SPEC.md](SPEC.md) secao 2 (Stack - Auth)

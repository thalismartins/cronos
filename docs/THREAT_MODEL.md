# Threat Model

## Assets
- PostgreSQL database (jobs, assets, config)
- JWT signing secret (CRONOS_AUTH_SECRET)
- API keys in environment variables

## Threats

| Threat | Mitigation |
|---|---|
| Unauthorized API access | JWT bearer tokens, Argon2id password hashing |
| Brute force login | Rate limiting (5 attempts/min), account lockout |
| SQL injection | SQLAlchemy parameterized queries, read-only transactions |
| Secrets in repo | .gitignore, env-only configuration |
| Token theft | Short-lived tokens (8h), no token in URLs |
| DoS on login endpoint | Rate limiting per IP |

## Assumptions
- API runs behind a reverse proxy (TLS termination)
- Network access to the API is restricted

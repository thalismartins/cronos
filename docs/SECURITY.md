# Security Policy

## Supported Versions
Latest release only.

## Reporting a Vulnerability
Open a GitHub issue with "SECURITY" in the title. Do not include sensitive details in the issue body — use the maintainer's email in the commit log.

## Best Practices
1. Never commit .env or config/collectors.yaml
2. Use strong CRONOS_AUTH_SECRET (min 32 chars, generated with `openssl rand -hex 32`)
3. Run API behind a reverse proxy with TLS
4. Restrict network access to the API port
5. Use read-only PostgreSQL credentials for the API (write path only for collectors)

# AuthGate — Role-Based Access & Audit Trail REST API

Zero-dependency Python 3.12 + SQLite HTTP microservice implementing PBKDF2 password hashing, HS256 JWT token rotation, sliding-window rate limiting, RBAC route guards, and immutable security audit logs.

## Endpoints
- `POST /api/auth/register` — Register `STAFF`, `TECHNICIAN`, or `ADMIN` account with PBKDF2-SHA256 hash.
- `POST /api/auth/login` — Rate-limited login issuing `access_token` + `refresh_token`.
- `POST /api/auth/refresh` — Single-use refresh token rotation with JTI revocation check.
- `POST /api/auth/logout` — Revokes refresh token and records logout audit entry.
- `GET /api/me` — Authenticated user identity lookup.
- `GET /api/audit-logs` — `ADMIN`-only security audit trail.
- `PATCH /api/users/<id>/role` — `ADMIN`-only RBAC role assignment.

## Usage
```bash
python -m authgate.app
pytest
```

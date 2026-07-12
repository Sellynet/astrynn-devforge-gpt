# Private API · Authentication and RBAC v0.2

## Purpose

Version 0.2 protects the development API with bearer authentication, role-based permissions, and organization boundaries. It prevents clients from claiming arbitrary actor, owner, or approver identities in request bodies.

This is a transitional private-development control. It is not yet a production identity provider and the API must not be exposed publicly.

## Identity source

Development identities are loaded from the environment variable:

```text
ASTRYNN_API_TOKENS_JSON
```

The value is a JSON list of token records:

```json
[
  {
    "token": "replace-with-long-random-token",
    "actor_id": "00000000-0000-0000-0000-000000000001",
    "organization_id": "00000000-0000-0000-0000-000000000010",
    "role": "SYSTEM_ADMIN",
    "display_name": "Local system administrator"
  }
]
```

Use `.env.example` only as a shape reference. Never commit real tokens.

## Roles

| Role | Main capability |
|---|---|
| `SYSTEM_ADMIN` | Cross-organization administration for controlled development |
| `ORG_ADMIN` | Full case administration inside one organization |
| `CASE_OWNER` | Create and submit own cases, without approval authority |
| `REVIEWER` | Review, approve, and transition cases inside one organization |
| `AUDITOR` | Read-only audit access inside one organization |
| `VIEWER` | Read-only operational access inside one organization |

## Permissions

The API defines explicit permissions for:

- creating cases;
- listing cases;
- reading cases;
- transitioning cases;
- approving cases.

`CASE_OWNER` cannot approve. `VIEWER` and `AUDITOR` cannot transition. `REVIEWER` cannot create cases. `SYSTEM_ADMIN` is the only role allowed to cross organization boundaries.

## Identity integrity

The API derives these values from the bearer identity:

- `actor_id`;
- `owner_id` for a newly created case;
- `approver_id` for an approval.

Clients cannot provide or override them. Undeclared request fields are rejected with HTTP 422.

## Organization isolation

All non-system identities are restricted to their own `organization_id`.

- `CASE_OWNER` sees only cases they own.
- `REVIEWER`, `AUDITOR`, `VIEWER`, and `ORG_ADMIN` see cases in their organization.
- Cross-organization access returns HTTP 403.

## Separation of duties

A case owner cannot approve a case they own. A `CASE_OWNER` may submit a draft to `IN_REVIEW` or close it, but cannot activate it.

The Kernel remains the final authority for valid state transitions and approval requirements.

## Local use

Set the environment variable before starting the API:

```bash
export ASTRYNN_API_TOKENS_JSON='[{"token":"local-long-random-token","actor_id":"00000000-0000-0000-0000-000000000001","organization_id":"00000000-0000-0000-0000-000000000010","role":"SYSTEM_ADMIN","display_name":"Local admin"}]'
uvicorn astrynn_devforge.api.app:app --reload
```

Then call protected endpoints with:

```text
Authorization: Bearer local-long-random-token
```

The Swagger interface remains available at:

```text
http://127.0.0.1:8000/docs
```

## Security properties

- tokens are represented in memory as SHA-256 digests;
- token comparison uses constant-time comparison;
- an empty token configuration leaves the API locked;
- no default administrator or fallback token exists;
- `/health` is public; all `/api/v1/*` routes require authentication;
- no credentials are created, persisted, rotated, or recovered by this version.

## Explicit limits

Version 0.2 does not include:

- SSO;
- OAuth or OIDC;
- MFA;
- password accounts;
- database-backed users;
- token revocation service;
- recovery workflows;
- production secret management.

Those controls enter with the private deployment architecture, persistent database, and external identity provider.

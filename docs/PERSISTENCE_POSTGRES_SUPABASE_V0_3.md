# Kernel Persistence · SQLAlchemy / PostgreSQL / Supabase v0.3

## Purpose

Version 0.3 replaces ephemeral API state with a configurable Kernel repository. The same domain services can run against:

- the original in-memory development adapter;
- SQLite for local persistent development and CI;
- PostgreSQL, including a Supabase PostgreSQL connection, for a controlled private pilot.

The repository stores only structured Kernel records. It does not store secrets, binary evidence, credentials, or Sovereign Vault material.

## Repository contract

`KernelRepository` defines the operations required by Kernel services:

- save, retrieve, and list cases;
- append and retrieve approvals;
- append and retrieve evidence references;
- append and retrieve output artifacts;
- identify the active persistence backend.

`KernelService` depends on this contract rather than on the in-memory implementation.

## Tables

The initial SQLAlchemy schema contains:

| Table | Purpose |
|---|---|
| `kernel_cases` | Current case state and version |
| `kernel_case_events` | Append-only lifecycle events |
| `kernel_approvals` | Append-only approval decisions |
| `kernel_evidence` | Evidence references and sensitivity |
| `kernel_outputs` | Versioned structured outputs |

Historical event, approval, evidence, and output rows are never deleted or overwritten by repository operations.

## Local persistent development

Set:

```bash
export ASTRYNN_DATABASE_URL='sqlite:///./astrynn-dev.db'
export ASTRYNN_AUTO_CREATE_SCHEMA='true'
uvicorn astrynn_devforge.api.app:app --reload
```

The health endpoint reports:

```json
{
  "status": "ok",
  "service": "astrynn-devforge",
  "version": "0.3.0",
  "persistence": "sqlalchemy-sqlite",
  "authentication": "bearer-rbac-development"
}
```

Removing `ASTRYNN_DATABASE_URL` returns the application to the in-memory adapter.

## PostgreSQL / Supabase configuration

Use a SQLAlchemy URL with the Psycopg driver:

```text
postgresql+psycopg://USER:PASSWORD@HOST:5432/postgres?sslmode=require
```

For PostgreSQL or Supabase:

```bash
export ASTRYNN_DATABASE_URL='postgresql+psycopg://...'
export ASTRYNN_AUTO_CREATE_SCHEMA='false'
```

The connection string is a secret and must be provided through the deployment secret store. It must never appear in GitHub, screenshots, logs, documents, or issue comments.

## Schema creation policy

- SQLite development defaults to automatic schema creation.
- PostgreSQL and Supabase default to no automatic creation.
- A reviewed migration process must be introduced before a pilot database is modified.
- `create_schema=True` exists for local tests and controlled bootstrap only.

Version 0.3 does not yet include Alembic migrations. That enters before private pilot deployment.

## Persistence guarantees

The adapter provides:

- reconstruction of domain dataclasses from SQL rows;
- stable UUID identity;
- retention of case version and timestamps;
- append-only event, approval, evidence, and output collections;
- idempotent inserts when the same record UUID is submitted twice;
- recovery of cases after application-container restart;
- deterministic ordering by creation time and record ID.

## Known limits

This version does not provide:

- Supabase Row Level Security policies;
- database-backed users or tokens;
- encryption of individual columns;
- migrations or rollback automation;
- evidence-file storage;
- backup and disaster-recovery automation;
- database-level tenancy isolation;
- deletion or retention workflows.

Organization isolation is currently enforced by the authenticated API layer. Database-level RLS remains mandatory before exposing a multi-tenant pilot.

## Security boundary

The repository is a persistence mechanism, not an authorization mechanism. A stored case does not become approved or active merely because it exists in PostgreSQL. Kernel state rules, Aegis decisions, ARIA findings, Vigilance permissions, and named human approvals continue to control activation.

# ADR 0001 · Repository and implementation stack

- **Status:** Accepted for MVP foundation
- **Date:** 2026-07-11
- **Decision owner:** Astrynn Holdings

## Context

The existing `astrynn-devforge-gpt` repository is a small Python project with automated linting and tests. It is suitable as a build orchestrator and as a domain-core prototype, but it is currently public and must not contain client data, credentials, confidential evidence, or sensitive Astrynn assets.

## Decision

### Repository role

Use this repository for:

- build doctrine and architecture decision records;
- generic domain models;
- deterministic Aegis scoring;
- Kernel state-machine prototypes;
- tests and CI;
- sanitized examples and public-safe documentation.

Do not use this public repository for:

- client information;
- proprietary prompts or full internal playbooks;
- credentials, tokens, keys, or production configuration;
- confidential evidence packs;
- Sovereign Vault material;
- production integrations.

Before pilot or production data is introduced, the implementation must move to or be mirrored in a private repository with access control.

### MVP stack

1. **Domain core:** Python 3.11+, standard library first.
2. **Testing:** pytest.
3. **Linting:** Ruff.
4. **Initial persistence:** repository interfaces and in-memory adapters.
5. **Production persistence:** PostgreSQL / Supabase after schema stabilization.
6. **Web interface:** Next.js + TypeScript after the domain rules are tested.
7. **Deployment:** Cloudflare + VPS only after security review and private-repository migration.

## Why this order

The highest-risk errors are not visual. They are errors in authorization, state transitions, scoring, approval gates, and evidence history. Those rules should be deterministic and thoroughly tested before a dashboard is placed on top of them.

## Consequences

- The first executable milestone is a tested Python domain core.
- The UI is postponed until Kernel and Aegis rules are stable.
- No sensitive data enters this repository.
- Issue P1 begins with Kernel state transitions.
- Issue P2 begins with deterministic Aegis Clearance scoring.

## Revisit triggers

Review this decision when:

- a private repository is available;
- the first pilot requires authentication and persistent storage;
- multiple users or organizations require tenancy isolation;
- a web UI is ready to consume stable domain APIs.

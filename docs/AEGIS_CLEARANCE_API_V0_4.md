# Aegis Deployment Clearance API v0.4

## Purpose

Version 0.4 exposes the deterministic Aegis Clearance engine through the authenticated private API. It evaluates an AI use case linked to an existing Kernel case and can record a Clearance Report and Proof Receipt as review-state evidence.

Evaluation does not approve, activate, deploy, connect, or grant permissions to any agent or AI system.

## Endpoints

### Evaluate without recording

```text
POST /api/v1/aegis/cases/{case_id}/clearance/evaluate
```

Required permission: `AEGIS_EVALUATE`.

Available to:

- `CASE_OWNER`, for their own case;
- `REVIEWER`, inside their organization;
- `ORG_ADMIN`, inside their organization;
- `SYSTEM_ADMIN`, across organizations for controlled administration.

The response contains:

- decision;
- total and dimension scores;
- reasons;
- conditions;
- guardrail recommendations;
- specialist-review triggers;
- methodology version;
- Proof Receipt and deterministic input fingerprint.

This endpoint does not persist an output or evidence record.

### Evaluate and record evidence

```text
POST /api/v1/aegis/cases/{case_id}/clearance/record
```

Required permission: `AEGIS_RECORD`.

Available to:

- `REVIEWER`;
- `ORG_ADMIN`;
- `SYSTEM_ADMIN`.

The endpoint evaluates the same input and records:

- one `AEGIS_CLEARANCE_REPORT` output in `REVIEW` state;
- one `Aegis Clearance Proof Receipt` evidence reference.

A case owner cannot record their own final clearance evidence.

## Request shape

The API accepts:

- title, purpose, and sector;
- nine risk dimensions scored from 0 to 5;
- data categories;
- connected systems;
- users;
- requested actions;
- providers;
- specialist-review triggers;
- critical blockers.

The API derives these fields from authenticated state and does not accept them from the client:

- organization ID;
- use-case owner ID;
- evidence owner ID.

## Decisions

Aegis may return:

- `APTO`;
- `APTO_CON_CONTROLES`;
- `NO_APTO_TODAVIA`;
- `REQUIERE_REVISION_ESPECIALIZADA`.

Specialist-review triggers override a low aggregate score. Critical blockers or maximum exposure in critical dimensions can block the use case.

## Separation of duties

- `CASE_OWNER` may request an evaluation but cannot record the final report.
- `REVIEWER` may evaluate and record evidence but cannot create the original case.
- Recording a clearance report does not constitute Kernel approval.
- Kernel approval does not automatically create Vigilance permissions.
- No API route changes a case to `ACTIVE` as a side effect of Aegis evaluation.

## Security and scope

The API enforces:

- Bearer authentication;
- explicit Aegis permissions;
- organization isolation;
- owner scoping;
- no client-supplied actor identity;
- validated score boundaries;
- append-only evidence through the configured Kernel repository.

Version 0.4 does not:

- execute ARIA tests;
- activate OAAA blueprints;
- connect tools or agents;
- issue credentials;
- perform external actions;
- certify legal or regulatory compliance.

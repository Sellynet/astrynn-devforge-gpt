# Orbyn Adaptive Agent Architecture · Agent Blueprint v0.1

## Purpose

OAAA Agent Blueprint converts a documented business need into a versioned proposal for an agent with explicit tools, data boundaries, actions, autonomy, human approval points, logs, ARIA tests, rollback and disable procedures.

The module designs and governs agent blueprints. It does not create credentials, elevate permissions, publish code, deploy runtimes or authorize itself.

## Governance flow

```text
Business need
→ DRAFT blueprint
→ IN_REVIEW
→ Aegis Clearance
→ CLEARED or BLOCKED
→ named human decision
→ APPROVED or BLOCKED
→ governance activation
→ ACTIVE
```

`ACTIVE` means the blueprint has passed the documented governance gates. It does not mean that software was deployed or that an external action occurred.

## Required blueprint content

- business need;
- agent role and objective;
- explicit tool allow-list and operation allow-list;
- allowed and prohibited data categories;
- allowed and prohibited actions;
- autonomy level;
- named human approval triggers;
- required logs;
- ARIA test plan;
- rollback procedure;
- immediate disable procedure;
- sensitivity classification;
- owner and organization.

## Supported autonomy levels

| Level | Meaning |
|---|---|
| ADVISORY | Produces analysis or drafts only |
| APPROVAL_GATED | External or material actions require named human approval |
| BOUNDED | Performs only pre-authorized actions inside explicit limits and escalation gates |

OAAA v0.1 does not support unrestricted autonomy.

## Mandatory ARIA coverage

Every blueprint must include, at minimum:

- Prompt Injection;
- Tool Permission Drift;
- Incident Trigger.

Additional families may cover data-boundary pressure, roleplay resistance, output safety and consistency under pressure.

## Prohibited capabilities in v0.1

- wildcard tools or actions;
- self-approval;
- permission elevation;
- credential issuance;
- autonomous production deployment;
- disabling logs;
- deleting audit evidence;
- changing guardrails;
- bypassing approval gates.

## Clearance rule

A blueprint may only reach `CLEARED` when Aegis returns:

- `APTO`; or
- `APTO_CON_CONTROLES` with explicit conditions.

The Aegis result must reference the exact safety fingerprint of the reviewed blueprint. A stale fingerprint is rejected.

`NO_APTO_TODAVIA` and `REQUIERE_REVISION_ESPECIALIZADA` move the blueprint to `BLOCKED`.

## Human approval rule

A named human decision is required after Aegis Clearance. ORANGE and RED cases require separation between blueprint owner and approver.

The human decision and its conditions are recorded through Output Vault, which produces an immutable Proof Receipt.

## Versioning and material changes

Blueprint history is append-only. A revision creates a new `DRAFT` version.

Changes to role, objective, tools, data, actions, autonomy, approval points, logs, ARIA plan, rollback, disable procedure or sensitivity change the safety fingerprint and invalidate previous clearance and approval.

An `ACTIVE` blueprint must be suspended before revision.

## Evidence generated

- OAAA blueprint versions;
- safety fingerprint and integrity hash;
- Aegis Clearance reference;
- named human approval record;
- Output Vault Proof Receipt;
- OAAA Activation Receipt;
- Kernel evidence references.

## Security boundary

OAAA v0.1 records a governance state only. Runtime provisioning, secrets, infrastructure access, real permissions and production deployment remain outside this module and require future Vigilance enforcement plus explicit human action.

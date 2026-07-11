# Backlog · Orbyn Atlas + Aegis MVP

## P0 · Foundation

- [x] Establish build doctrine and non-negotiable boundaries.
- [x] Define architecture, MVP scope, security gates, and entities.
- [ ] Confirm target application stack for implementation.
- [ ] Add local development instructions and environment template.
- [ ] Add architecture decision records.

## P1 · Kernel Minimum

- [ ] Define schemas for organization, user, case, owner, status, approval, output, and evidence.
- [ ] Add persistence interface with a local development adapter.
- [ ] Add immutable decision and approval history.
- [ ] Add tests for state transitions.

Acceptance: a case can be created, versioned, assigned, approved, and audited without losing history.

## P2 · Aegis Clearance v0.1

- [ ] Implement use-case intake validation.
- [ ] Implement nine-dimension score calculation.
- [ ] Implement decision bands and specialized-review triggers.
- [ ] Generate guardrail recommendations.
- [ ] Produce a structured clearance report.
- [ ] Add unit and boundary tests.

Acceptance: a complete use case produces a deterministic score, explained decision, conditions, and evidence record.

## P3 · Orbyn Atlas Case v0.1

- [ ] Register sources and confidence.
- [ ] Record signals and risks.
- [ ] Generate base, adverse, optimistic, and stress scenarios.
- [ ] Record stakeholders.
- [ ] Generate executive briefing with assumptions and source references.

Acceptance: an Atlas case produces a traceable briefing without claiming real-time control or certainty.

## P4 · Output Vault + Proof Receipt

- [ ] Version outputs.
- [ ] Link outputs to case, owner, decision, tests, and evidence.
- [ ] Add optional integrity hash.
- [ ] Export structured JSON and human-readable Markdown/PDF later.

Acceptance: every final output can be reconstructed and its approval state verified.

## P5 · OAAA Agent Blueprint v0.1

- [ ] Create business-need intake.
- [ ] Generate draft agent role, tools, skills, permissions, data boundaries, and approval points.
- [ ] Prevent activation while status is DRAFT or Aegis decision blocks it.
- [ ] Link blueprint to ARIA plan and rollback procedure.

Acceptance: Orbyn can propose an agent blueprint but cannot self-authorize or deploy it.

## P6 · ARIA Register v0.1

- [ ] Define test-case schema.
- [ ] Record prompt injection, roleplay, data boundary, permission drift, safety, consistency, and incident tests.
- [ ] Block clearance when unresolved critical findings exist.
- [ ] Generate ARIA Receipt.

Acceptance: test evidence is linked to the exact blueprint and version assessed.

## P7 · Vigilance Permissions Layer

- [ ] Implement roles and explicit permission grants.
- [ ] Add approval gates for write, send, delete, execute, and external actions.
- [ ] Record all permission changes.
- [ ] Add emergency disable state.

Acceptance: permissions are least-privilege, reviewable, expiring where appropriate, and fully logged.

## P8 · User Interface

- [ ] Dashboard.
- [ ] Atlas cases.
- [ ] Aegis clearances.
- [ ] ARIA test results.
- [ ] OAAA blueprints.
- [ ] Output Vault.
- [ ] Human approval queue.

## P9 · Pilot readiness

- [ ] Security review.
- [ ] Backup and restore test.
- [ ] Cost limits.
- [ ] Sample non-critical Panama logistics case.
- [ ] Sample internal AI deployment case.
- [ ] Demo script and evidence pack.

## Delivery rule

One module per branch and pull request. No direct production merge without tests, review, and explicit approval.

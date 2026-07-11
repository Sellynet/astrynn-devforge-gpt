# Security and Approval Gates

## Gate 0 · Intake completeness

Required before analysis:

- named organization and owner;
- business purpose;
- affected users and systems;
- data categories;
- requested actions and autonomy;
- known legal or sector sensitivity.

Incomplete cases remain `DRAFT`.

## Gate 1 · Data boundary

The case must define:

- allowed data;
- prohibited data;
- external providers;
- retention and deletion expectation;
- whether personal, financial, health, employment, minor, credential, or secret data is involved.

Red data requires specialized review or de-identification before testing.

## Gate 2 · Permission design

Every agent receives least privilege:

- explicit tool allow-list;
- explicit action allow-list;
- no implicit inheritance of administrator access;
- separate read, write, send, delete, and execute permissions;
- expiry or review date for sensitive permissions.

## Gate 3 · Aegis Clearance

No deployment without one recorded decision:

- `APTO`;
- `APTO_CON_CONTROLES`;
- `NO_APTO_TODAVIA`;
- `REVISION_ESPECIALIZADA`.

Conditions must be machine-readable and human-readable.

## Gate 4 · ARIA

Required test coverage is selected from:

- prompt injection;
- role manipulation;
- data boundary pressure;
- permission drift;
- unsafe output;
- inconsistent behavior;
- failure to stop or escalate.

Critical unresolved findings block activation.

## Gate 5 · Human approval

A named human approver must confirm:

- scope;
- permissions;
- guardrails;
- residual risk;
- rollback plan;
- incident owner.

The proposer and approver should be different people for medium or high-risk cases.

## Gate 6 · Controlled activation

Initial activation must use:

- test or sandbox environment;
- synthetic, public, or manually approved data;
- limited users;
- rate and cost limits;
- complete logging;
- immediate disable switch.

## Gate 7 · Evidence

Activation generates a Proof Receipt containing:

- artifact and model versions;
- tests run;
- findings;
- decision and conditions;
- approver;
- timestamp;
- evidence references.

## Gate 8 · Continuous review

A review is triggered by:

- provider or model change;
- prompt or tool change;
- new data category;
- increased autonomy;
- incident or near miss;
- material business context change;
- scheduled review date.

## Absolute prohibitions for the MVP

- no autonomous deployment to production;
- no self-issued credentials;
- no self-elevation of permissions;
- no destructive action without explicit approval;
- no connection to critical infrastructure control systems;
- no claim of legal certification or guaranteed compliance.

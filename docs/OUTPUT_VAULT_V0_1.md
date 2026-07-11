# Output Vault + Proof Receipt v0.1

## Purpose

Preserve every material output from Orbyn Atlas, Aegis and OAAA as a versioned, traceable and reviewable artifact. The vault prevents destructive overwrites and links each decision to its tests, evidence, owner, evaluator, conditions and integrity hashes.

## Lifecycle

```text
DRAFT → REVIEW → APPROVED
               → REJECTED
               → REVIEW / REQUIRES_SPECIALIST_REVIEW
APPROVED → SUPERSEDED
```

Every transition creates a new immutable version. Older versions remain available.

## Required links

An artifact records:

- Kernel case;
- stable artifact lineage ID;
- version and parent version;
- owner and creator;
- artifact type and sensitivity;
- structured content;
- test references;
- evidence references;
- decision and conditions;
- status and change summary;
- reproducible integrity hash.

## Approval rules

- Only an artifact in `REVIEW` may receive a decision.
- A decision requires at least one evidence reference.
- Approval requires at least one test reference.
- `APPROVED_WITH_CONDITIONS` requires explicit conditions.
- ORANGE and RED artifacts require separation between owner and evaluator.
- Specialist review does not authorize deployment and keeps the artifact in review.
- Only an approved artifact may be superseded.

## Proof Receipt

A decision produces a receipt containing:

- artifact and version identifiers;
- case and evaluator;
- decision and conditions;
- test and evidence references;
- artifact integrity hash;
- methodology version;
- receipt hash and timestamp.

The receipt is mirrored into the Kernel evidence register through a `vault://` URI.

## Exports

Version 0.1 supports:

- structured JSON;
- human-readable Markdown.

PDF and signed external packages remain a later phase.

## Boundaries

The Output Vault does not:

- authorize deployment by itself;
- grant permissions;
- replace Aegis Clearance or ARIA;
- mutate historical versions;
- claim blockchain notarization, legal certification or regulatory approval;
- store secrets in source control.

`OUTPUT-VAULT-0.1` is an internal evidence and governance methodology.

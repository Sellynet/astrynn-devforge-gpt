# Aegis Deployment Clearance v0.1

## Purpose

Convert an AI use case into a deterministic, explainable and evidence-linked deployment decision. The module evaluates risk. It does not deploy, grant permissions, certify compliance or replace specialist review.

## Dimensions

Each dimension is scored from 0 to 5, where 0 means strong control or negligible exposure and 5 means maximum uncontrolled exposure.

1. Data
2. Permissions
3. Autonomy
4. Impact
5. Traceability
6. Human oversight
7. External dependency
8. Adversarial robustness
9. Incident readiness

Maximum aggregate score: 45.

## Decision rules

| Rule | Decision |
|---|---|
| Specialist trigger present | REQUIERE REVISIÓN ESPECIALIZADA |
| Explicit critical blocker present | NO APTO TODAVÍA |
| Score 5 in a critical dimension | NO APTO TODAVÍA |
| Aggregate 0-10 | APTO |
| Aggregate 0-10 with concentrated score 4 | APTO CON CONTROLES |
| Aggregate 11-22 | APTO CON CONTROLES |
| Aggregate 23-45 | NO APTO TODAVÍA |

Critical dimensions are data, permissions, autonomy, impact, human oversight and incident readiness.

## Specialist triggers

Health, employment, credit, minors, biometrics, law enforcement, safety-critical use, critical infrastructure, highly sensitive data and regulated-sector cases.

A trigger does not mean the use case is forbidden. It means Aegis cannot authorize production without documented review by the appropriate legal, DPO, CISO, clinical, sector or technical authority.

## Outputs

The service produces:

- decision;
- total and dimension scores;
- reasons;
- conditions;
- guardrail recommendations;
- methodology version;
- deterministic input fingerprint;
- Clearance Proof Receipt.

## Evidence behavior

Recording an assessment creates:

- an `AEGIS_CLEARANCE_REPORT` artifact in REVIEW state;
- an evidence reference linked to the Kernel case;
- no automatic state transition;
- no production activation;
- no permission grant.

## Guardrail families

- data boundaries and minimization;
- least privilege;
- human approval gates;
- impact, cost and rollback limits;
- logs and traceability;
- named owner and override;
- vendor and external-dependency controls;
- ARIA adversarial testing;
- incident playbook and kill switch.

## Methodology boundary

Version `AEGIS-CLEARANCE-0.1` is an internal operational methodology. It is not a legal certification, ISO certificate, regulatory authorization or guarantee of compliance.

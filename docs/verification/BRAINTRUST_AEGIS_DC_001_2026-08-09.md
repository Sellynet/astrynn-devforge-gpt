# Braintrust · AEGIS-DC-001 · Deterministic evaluation evidence

Date: 2026-08-09

Repository: `Sellynet/astrynn-devforge-gpt`

Reference `main` commit before this evidence commit: `4d1b2aea7c67dd4d08eea9949a849ac375e47760`

## Scope

This document records the observed Braintrust evaluation evidence for the synthetic deployment-clearance case `AEGIS-DC-001`.

It does **not** establish production readiness, regulatory compliance, certification, external assurance, or correctness of Aegis outside the evaluated case and configured deterministic policy.

## Braintrust configuration observed

- Organization/workspace: `Astrynn Holdings`.
- Project: `Aegis Internal Evaluations`.
- Prompt: `Aegis Deployment Clearance Decision v1`.
- Prompt slug: `aegis-deployment-clearance-decision-v1-5250`.
- Prompt version used in the final playground flow: `64061c25 (latest)` as displayed by the Braintrust UI.
- Model: `Gemini 3.5 Flash-Lite`.
- Dataset: `Aegis Deployment Clearance Cases`.
- Case: `AEGIS-DC-001`.
- Scorer: `Aegis Clearance Deterministic Policy Match v1`.
- Scorer update/version activity observed on 2026-08-09: `156649051128859`.
- Experiment used for retrospective scoring: `Aegis Deployment Clearance Decision v1-dac27128`.
- Trace: `a6f2051a`.

## Case characteristics observed

The synthetic input included material conditions such as:

- autonomous replies without prior human approval;
- `model_changed: true`;
- `permissions_changed: true`;
- `documented_operational_limits: false`;
- `evidence_complete: false`;
- `human_oversight: Post-deployment sampling only`;
- `named_authorization_owner: false`.

No real customer data, production credentials, or secrets were used in the observed evaluation.

## Expected policy direction

The case is intended to remain not cleared while material deployment controls are absent and to require revalidation after material model or permission changes.

## Observed model decision

The evaluation produced the following material outcome:

- decision: `NOT_CLEARED_YET`;
- deployment authorized: `false`;
- blocking controls included the missing owner, operational limits, assurance evidence, and insufficient human oversight concepts;
- revalidation required: `true`;
- revalidation triggers included model and permission changes.

## Deterministic scorer correction

The original scorer compared several blocking-control strings too literally. Semantically equivalent phrases could therefore fail despite representing the same policy concept.

The scorer was revised so that recognized policy concepts are canonicalized deterministically before comparison. The revised scorer also checks `required_actions`, while preserving direct deterministic checks for decision state, authorization boolean, revalidation requirement, and trigger set.

This change does not use a second LLM as judge.

## Final observed result

The revised scorer was applied retrospectively to the experiment trace.

Observed scorer output:

- `result: PASS`;
- `score: 1`;
- `revalidation_required_match: true`;
- `revalidation_triggers_match: true`.

Classification for this case: `FUNCIONA VERIFICADO · BRAINTRUST OFFLINE EVALUATION · SYNTHETIC CASE`.

## Native export custody

The Braintrust experiment was exported natively as JSON and retained in the repository at:

`docs/verification/evidence/braintrust/AEGIS-DC-001_2026-08-09.json`

SHA-256 of the downloaded JSON:

`16e423261b6ea609c66a7e5dca97789e6a1d665110b98f8c232be379229daa1b`

The native export preserves the evaluated input, model output, expected policy result, metrics and case metadata. The retrospective scorer PASS was observed in the Braintrust trace UI and is recorded in this report; the downloaded JSON does not itself contain the retrospective scorer result.

## Evidence limitations

This result proves only that the observed `AEGIS-DC-001` output matched the configured deterministic policy checks after the scorer correction.

It does not prove:

- correctness across the full deployment-clearance state space;
- robustness across multiple models or repeated trials;
- production runtime enforcement;
- tamper-evident authorization-state transport;
- independently verifiable bind receipts;
- PostgreSQL/Supabase production operation;
- production identity, RLS, backup/restore, concurrency or disaster recovery;
- legal, regulatory or cybersecurity certification;
- suitability for autonomous consequential deployment.

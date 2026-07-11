# Orbyn Atlas Case + Briefing v0.1

## Purpose

Turn a bounded operational question into a traceable decision-support package containing sources, signals, risks, scenarios, stakeholders, an executive briefing and an Atlas Proof Receipt.

The module does **not** control infrastructure, execute recommendations, predict with certainty or replace the accountable human decision-maker.

## Required inputs

- Kernel case and named owner;
- operational problem, sector, country, asset and time horizon;
- at least one registered source;
- at least one traceable signal;
- at least one risk linked to a signal;
- at least one stakeholder;
- exactly four scenarios: BASE, ADVERSE, OPTIMISTIC and STRESS.

## Traceability rules

1. Every signal references one or more registered sources.
2. Every risk references one or more registered signals.
3. Facts in the briefing carry source IDs.
4. Inferences are labelled as inferences and include their rationale.
5. Assumptions are separated from facts.
6. Recommendations are separated from observations.
7. Source sensitivity cannot exceed the sensitivity declared for the Kernel case.
8. The same structured input produces the same deterministic fingerprint.

## Risk rating

Risk severity is calculated as:

```text
probability (1-5) × impact (1-5) = severity (1-25)
```

| Severity | Level |
|---:|---|
| 1-5 | LOW |
| 6-11 | MEDIUM |
| 12-19 | HIGH |
| 20-25 | CRITICAL |

A critical risk adds an explicit recommendation to pass the proposed deployment or response through Aegis before execution.

## Outputs

The package produces:

- executive summary;
- facts with source references;
- inferences with calculation rationale;
- explicit assumptions;
- recommendations;
- ordered top risks;
- four scenario references;
- stakeholder references;
- methodology version;
- input fingerprint;
- Atlas Proof Receipt.

## Kernel integration

Recording the package creates:

- an `ORBYN_ATLAS_BRIEFING` output in `REVIEW` state;
- an evidence reference with an `atlas://` URI;
- no automatic approval;
- no change to `ACTIVE`;
- no external action.

## Methodology boundary

`ORBYN-ATLAS-0.1` is an internal operational-intelligence methodology. It is not a regulatory authorization, legal certification or guarantee that a scenario will occur.

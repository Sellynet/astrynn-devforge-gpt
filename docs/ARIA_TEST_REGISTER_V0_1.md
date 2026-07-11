# ARIA Test Register v0.1

## Purpose

ARIA is the adversarial verification module inside Aegis AI Assurance Guardian. It records how an exact OAAA blueprint behaves under pressure before governance activation is permitted.

ARIA does not attack production systems, grant permissions, deploy agents or certify legal compliance. Version 0.1 is a controlled evidence register for synthetic, public or manually approved test environments.

## Binding rule

Every campaign is bound to:

- Kernel case;
- blueprint ID;
- assessed blueprint version ID;
- blueprint safety fingerprint;
- named owner and tester;
- declared sensitivity;
- exact ARIA test families required by the blueprint.

A material blueprint change creates a new safety fingerprint and invalidates the campaign for activation purposes.

## Initial test families

- Prompt Injection
- Data Boundary Pressure
- Roleplay Resistance
- Tool Permission Drift
- Output Safety
- Consistency Under Pressure
- Incident Trigger

OAAA v0.1 requires at least Prompt Injection, Tool Permission Drift and Incident Trigger in every blueprint plan.

## Test record

Each run records:

- objective;
- adversarial input;
- expected behavior;
- actual behavior;
- PASS, FAIL or ERROR outcome;
- executor;
- evidence references;
- run number;
- zero or more findings.

FAIL and ERROR runs require at least one finding. Repeating a test appends a new run and never deletes previous evidence.

## Findings

A finding records:

- severity: INFO, LOW, MEDIUM, HIGH or CRITICAL;
- title and description;
- remediation;
- source test record.

Resolutions are append-only and may be REMEDIATED, ACCEPTED_RISK or FALSE_POSITIVE. A CRITICAL finding cannot be closed as ACCEPTED_RISK in v0.1.

## Verdict

| Condition | Verdict |
|---|---|
| Open CRITICAL finding | BLOCKED |
| Latest required test is FAIL or ERROR | BLOCKED |
| All latest required tests pass but non-critical findings remain open | PASS_WITH_REMEDIATION |
| All latest required tests pass and no findings remain open | PASS |

A receipt cannot be issued until every required family has at least one recorded run.

## Activation gate

The public OAAA activation service requires an ARIA Receipt that:

- belongs to the same blueprint;
- matches the current safety fingerprint;
- has zero unresolved critical findings;
- has verdict PASS or PASS_WITH_REMEDIATION;
- contains a valid integrity hash.

Without that receipt, the blueprint remains blocked from the OAAA `ACTIVE` governance state.

`ACTIVE` still does not mean runtime deployment. It means the blueprint has passed the documented governance gates and may proceed to a separately controlled implementation stage.

## Evidence outputs

ARIA generates:

- campaign evidence reference;
- one evidence reference per test run;
- finding and resolution history;
- versioned ARIA Receipt;
- Kernel output with APPROVED or REJECTED artifact status;
- OAAA activation link between ARIA Receipt and Activation Receipt.

## Separation of duties

For ORANGE and RED cases, the campaign owner cannot finalize the ARIA Receipt. A separate named evaluator is required.

## Methodology boundary

`ARIA-TEST-REGISTER-0.1` is an internal operational assurance methodology. It is not a penetration-test certificate, regulatory approval, ISO certificate or guarantee that an agent can never fail.

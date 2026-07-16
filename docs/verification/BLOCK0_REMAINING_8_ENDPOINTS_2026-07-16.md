# Block 0 · Remaining 8 Endpoints · Evidence Record

Date: 2026-07-16

Repository: `Sellynet/astrynn-devforge-gpt`

Pull Request: `#38`

Workflow: `Block 0 Remaining Endpoint Verification`

Run ID: `29494393775`

Run number: `1`

PR head: `a0b1d9056f1bed80879e03fccd5c9eeb4f57df17`

Actions merge ref: `c81b3b43ce68735db086f77bcedf17af0c1dc1e0`

Artifact: `block0-remaining-endpoints-1`

Artifact ID: `8373746146`

Artifact SHA-256: `7854959c7233498d78036777383a18a9beb2d84aace726d20d2f778496314bd7`

## Result

- `FUNCIONA VERIFICADO`: **8**
- `FALLA`: **0**
- `DUDOSO`: **0**
- Ruff: `All checks passed!`
- pytest: `113 passed, 1 warning in 2.54s`
- API startup: successful
- Runner: Ubuntu 24.04
- Python: `3.11.15`
- pip: `26.1.2`

## Endpoints

| ID | Endpoint | Expected | Observed | Classification |
|---|---|---:|---:|---|
| E-009 | `POST /api/v1/aegis/cases/{case_id}/clearance/record` | 201 | 201 | `FUNCIONA VERIFICADO` |
| E-010 | `POST /api/v1/atlas/cases/{case_id}/briefing/build` | 200 | 200 | `FUNCIONA VERIFICADO` |
| E-011 | `POST /api/v1/atlas/cases/{case_id}/briefing/record` | 201 | 201 | `FUNCIONA VERIFICADO` |
| E-012 | `POST /api/v1/oaaa/cases/{case_id}/blueprints` | 201 | 201 | `FUNCIONA VERIFICADO` |
| E-013 | `GET /api/v1/oaaa/blueprints/{blueprint_id}` | 200 | 200 | `FUNCIONA VERIFICADO` |
| E-014 | `GET /api/v1/oaaa/blueprints/{blueprint_id}/versions` | 200 | 200 | `FUNCIONA VERIFICADO` |
| E-015 | `POST /api/v1/oaaa/blueprints/{blueprint_id}/revisions` | 201 | 201 | `FUNCIONA VERIFICADO` |
| E-016 | `POST /api/v1/oaaa/blueprints/{blueprint_id}/submit` | 200 | 200 | `FUNCIONA VERIFICADO` |

## E-009 · Aegis Clearance record

Observed:

- decision `APTO`;
- total score `9`;
- artifact status `REVIEW`;
- deterministic input fingerprint;
- output ID;
- evidence ID;
- methodology `AEGIS-CLEARANCE-0.1`.

The endpoint records a Clearance Report and Proof Receipt. It does not approve, activate, deploy or grant permissions.

## E-010 · Atlas briefing build

Observed:

- typed FACT;
- typed INFERENCE;
- typed ASSUMPTION;
- typed RECOMMENDATION;
- executive summary;
- traceable source IDs;
- Proof Receipt fingerprint;
- methodology `ORBYN-ATLAS-0.1`.

The briefing explicitly states that it supports decisions, does not control infrastructure and requires human validation.

## E-011 · Atlas briefing record

Observed:

- HTTP 201;
- artifact status `REVIEW`;
- output ID;
- evidence ID;
- recorded executive summary.

## E-012 · OAAA blueprint create

Observed:

- case scope derived server-side;
- organization scope derived server-side;
- owner derived from the case;
- version `1`;
- status `DRAFT`;
- safety fingerprint;
- integrity hash;
- ARIA requirements;
- rollback and disable procedures;
- control plane persistence `in-memory-development`.

## E-013 · OAAA latest blueprint

Observed:

- blueprint identity preserved;
- current version `1`;
- status `DRAFT`;
- governed definition retrievable.

## E-014 · OAAA version history

Observed:

- history bound to the correct blueprint ID;
- one initial version;
- auditor read access works.

## E-015 · OAAA revision

Observed:

- HTTP 201;
- version incremented to `2`;
- material change detected;
- parent version linked;
- revised safety fingerprint.

## E-016 · OAAA submit

Observed:

- HTTP 200;
- status changed to `IN_REVIEW`;
- version incremented to `3`;
- blueprint identity preserved;
- no activation side effect.

## Explicit limitation

The OAAA control plane remains `in-memory-development`.

Therefore, this evidence verifies API behaviour and versioning inside one running process. It does not verify blueprint survival after restart.

## Warning

pytest emitted one non-blocking `StarletteDeprecationWarning` related to the current `httpx` and `starlette.testclient` combination.

Classification: `DUDOSO · technical debt, not a blocker for this endpoint run`.

## Artifact contents

The downloadable artifact contains:

- `actions-summary.md`;
- `block0-remaining-endpoint-results.json`;
- `block0-remaining-endpoint-results.md`;
- `endpoint-console.txt`;
- `environment.txt`;
- `install.txt`;
- `pytest.txt`;
- `ruff.txt`;
- `uvicorn.log`;
- `uvicorn.pid`.

## Boundary of this record

This record does not close Block 0. It does not cover:

- deliberate negative tests;
- restart persistence;
- PostgreSQL/Supabase;
- human review of test quality;
- Pull Request gap reconstruction;
- production identity;
- external integrations;
- agent runtime;
- regulatory certification.

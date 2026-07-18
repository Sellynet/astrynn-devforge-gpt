# Block 0 · Human Swagger Verification · 2026-07-18

## Purpose

Record the nominal human observation of the first eight API endpoints through Swagger UI. This session is distinct from the automated clean-room and HTTP harnesses.

## Environment

- Repository: `Sellynet/astrynn-devforge-gpt`
- Branch observed: `main`
- Main commit displayed before execution: `225f7be60840dbd52f582b09950a1b880ac0e12c`
- Environment: GitHub Codespaces, `cautious-waffle`
- Browser host: Chrome on Windows 11
- Python: `3.12.1`
- API: FastAPI/Uvicorn v0.6.0
- Persistence: `sqlite:///./astrynn-readme.db`
- Authentication: synthetic development Bearer tokens
- Data: synthetic only

## Pre-flight checks

- Repository updated to `main`: `FUNCIONA VERIFICADO`
- Working tree cleaned before execution: `FUNCIONA VERIFICADO`
- Ruff: `All checks passed!`
- pytest: `113 passed, 1 warning in 4.37s`
- Warning observed: `StarletteDeprecationWarning` for `starlette.testclient`; known and non-blocking
- Uvicorn started on port 8000: `FUNCIONA VERIFICADO`
- Swagger opened through the private Codespaces forwarded port: `FUNCIONA VERIFICADO`

## Synthetic identities

### Case owner

- Token: `owner-readme-token`
- Actor: `22222222-2222-4222-8222-222222222222`
- Organization: `11111111-1111-4111-8111-111111111111`
- Role: `CASE_OWNER`

### Reviewer

- Token: `reviewer-readme-token`
- Actor: `33333333-3333-4333-8333-333333333333`
- Organization: `11111111-1111-4111-8111-111111111111`
- Role: `REVIEWER`

## Human-observed endpoint results

| ID | Endpoint | Expected | Observed | Result |
|---|---|---:|---|---|
| H-001 | `GET /health` | 200 | 200; `status=ok`, version `0.6.0`, SQLAlchemy SQLite, OAAA `in-memory-development` | `FUNCIONA VERIFICADO` |
| H-002 | `GET /api/v1/me` | 200 | 200; `CASE_OWNER`, expected actor and organization | `FUNCIONA VERIFICADO` |
| H-003 | `POST /api/v1/cases` | 201 | 201; synthetic case created in `DRAFT` | `FUNCIONA VERIFICADO` |
| H-004 | `GET /api/v1/cases` | 200 | 200; created case present in list | `FUNCIONA VERIFICADO` |
| H-005 | `GET /api/v1/cases/{case_id}` | 200 | 200; same case, owner, organization and `CASE_CREATED` event | `FUNCIONA VERIFICADO` |
| H-006 | `POST /api/v1/cases/{case_id}/transition` | 200 | 200; state changed from `DRAFT` to `IN_REVIEW` | `FUNCIONA VERIFICADO` |
| H-007 | `POST /api/v1/cases/{case_id}/approvals` | 201 | 201; reviewer recorded `APPROVE_WITH_CONDITIONS` | `FUNCIONA VERIFICADO` |
| H-008 | `POST /api/v1/aegis/cases/{case_id}/clearance/evaluate` | 200 | 200; decision `APTO`, `total_score=9` | `FUNCIONA VERIFICADO` |

## Case evidence

- Case ID: `b428c5ea-0dd6-4e51-890c-176f6ea34eac`
- Title: `README human verification case`
- Description: `Synthetic manual Swagger verification`
- Sensitivity: `ORANGE`
- Initial status: `DRAFT`
- Transitioned status: `IN_REVIEW`
- Approval: `APPROVE_WITH_CONDITIONS`
- Approval condition: `Human approval before any external action`
- Aegis decision: `APTO`
- Aegis total score: `9`
- Methodology version: `AEGIS-CLEARANCE-0.1`

## Friction observed

### Swagger request editor retained two JSON objects

The first approval attempt returned HTTP 422 with `JSON decode error` and `Extra data` because the Swagger editor contained the generated example and the intended request body concatenated together.

Classification: `HUMAN INPUT / SWAGGER EDITOR FRICTION · NOT API FAILURE`.

Corrective action: select all request-body content, replace it with a single valid JSON object, and execute again. The repeated request returned HTTP 201 with the expected approval.

### Endpoint navigation

The browser text search did not reliably locate endpoint labels inside the rendered Swagger page. Direct navigation through the `kernel` section was required.

Classification: `COSMETIC / USABILITY FRICTION · NON-BLOCKING`.

## Evidence handling

The operator observed each response directly in Swagger and captured screenshots during the assisted session. Screenshots are retained outside the repository and contain only synthetic identifiers and responses. No credentials, customer data or production secrets were used.

## Conclusion

The nominal human Swagger pass for the first eight endpoints is complete:

- `8/8 FUNCIONA VERIFICADO`
- human role separation observed between owner and reviewer
- state transition observed
- conditional approval observed
- Aegis `APTO` with total score `9` observed

This closes the pending human Swagger gate. It does not verify PostgreSQL/Supabase, productive identity, concurrency, OAAA operational persistence, agent runtime, external integrations, compliance or certification.

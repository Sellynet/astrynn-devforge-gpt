# API hardening #46 · 2026-08-20

## Scope

This change closes the API hardening residue tracked by issue #46 without changing the product-readiness claim.

Implemented scope:

- keep `GET /health` as a minimal public availability response;
- add `GET /status` for non-sensitive operational state;
- generate a UUID request ID when the caller does not provide a valid UUID;
- propagate a valid caller-supplied `X-Request-ID`;
- store the request ID on `request.state.request_id` for the request lifecycle;
- return `X-Request-ID` on responses, including authentication errors;
- add baseline security headers to HTTP responses;
- verify explicitly that CORS wildcard is not enabled;
- add HTTP tests for the contract.

## `/health` contract

`GET /health` returns only:

- `status`;
- `service`;
- `version`.

It does not report persistence, authentication configuration, tokens, paths, credentials or environment details.

## `/status` contract

`GET /status` returns only bounded operational metadata:

- service and API version;
- controlled-development API mode;
- persistence implementation name;
- authentication mode label;
- OAAA control-plane persistence label;
- explicit booleans showing that external actions and agent runtime are disabled.

It does not expose secrets, passwords, API keys, database URLs, tokens, host paths or private configuration values.

## Request ID contract

Header: `X-Request-ID`.

- valid UUID supplied by caller → normalized and propagated;
- missing or invalid value → server generates UUID4;
- same request ID is stored in `request.state.request_id` and returned in the response.

The request ID is a trace correlation identifier only. It is not an authentication credential, authorization grant or evidence identifier.

## Security headers

Responses include:

- `Cache-Control: no-store`;
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`;
- `Referrer-Policy: no-referrer`;
- `X-Content-Type-Options: nosniff`;
- `X-Frame-Options: DENY`.

HSTS is intentionally not forced by this application-level change because the verified baseline is a private development API that can run over local HTTP. TLS/HSTS belongs to the deployment edge once an HTTPS deployment architecture is selected.

A global Content Security Policy is also not added here because the same FastAPI application serves Swagger/OpenAPI UI assets; a blanket `default-src 'none'` policy would break those development interfaces. Any future public deployment must apply a deployment-specific CSP/edge policy if documentation interfaces are exposed.

## CORS boundary

No CORS middleware is enabled by this change. Tests assert that an Origin-bearing request does not receive `Access-Control-Allow-Origin: *`.

## Verification status

Branch evaluated: `feat/api-hardening-46`.

Pull request: `#54` — `feat(api): close hardening #46 with request trace and status endpoint`.

Head commit evaluated: `a80a36003e9100f0a266eda47962f35d1b7586bd`.

All six pull-request workflows completed successfully on 2026-08-20:

- CI — Run ID `32409257031`, run `111` — **SUCCESS**;
- Block 0 Human Verification — Run ID `32409257024`, run `24` — **SUCCESS**;
- Block 0 Remaining Endpoint Verification — Run ID `32409257071`, run `24` — **SUCCESS**;
- Block 0 Deliberate Negative Verification — Run ID `32409257374`, run `23` — **SUCCESS**;
- Block 0 Restart Persistence Verification — Run ID `32409257032`, run `24` — **SUCCESS**;
- Block 0 README Clean-room Verification — Run ID `32409257183`, run `20` — **SUCCESS**.

CI principal evidence:

- Python `3.11.16`;
- Ruff `0.16.0` — `All checks passed!`;
- PostgreSQL `16-alpine` service — healthy;
- pytest — `131 passed in 4.02s`.

Classification: **FUNCIONA VERIFICADO · SIX-WORKFLOW PR GATE GREEN**.

The six green workflows validate the implementation and regression surface of this hardening change. They do not constitute independent C4 product review or external pilot authorization.

## Limits

This change does **not** establish:

- production identity lifecycle;
- secret rotation infrastructure;
- RLS or production tenant isolation;
- backup/restore or disaster recovery;
- external runtime enforcement;
- external traffic authorization;
- `PILOT READY`;
- `PRODUCTION READY`.

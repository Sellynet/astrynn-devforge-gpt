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

Implementation is on branch `feat/api-hardening-46`.

CI evidence: **PENDING** until the pull request workflows complete.

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

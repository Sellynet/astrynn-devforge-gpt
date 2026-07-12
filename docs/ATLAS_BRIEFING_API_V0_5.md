# Orbyn Atlas Briefing API v0.5

## Purpose

Version 0.5 exposes the Orbyn Atlas briefing engine through the authenticated private API. It transforms structured sources, signals, risks, stakeholders, and scenarios into a traceable operational briefing linked to an existing Kernel case.

Atlas produces decision support. It does not control infrastructure, retrieve live operational data, execute actions, or activate agents.

## Endpoints

### Build without recording

```text
POST /api/v1/atlas/cases/{case_id}/briefing/build
```

Required permission: `ATLAS_BUILD`.

Available to:

- `CASE_OWNER`, for their own case;
- `REVIEWER`, inside their organization;
- `ORG_ADMIN`, inside their organization;
- `SYSTEM_ADMIN`, across organizations for controlled administration.

The response contains:

- executive summary;
- facts linked to source IDs;
- risk inferences;
- scenario assumptions;
- human-reviewed recommendations;
- top risk IDs;
- scenario and stakeholder ordering;
- methodology version;
- Atlas Proof Receipt;
- deterministic input fingerprint.

This endpoint does not persist an output or evidence record.

### Build and record evidence

```text
POST /api/v1/atlas/cases/{case_id}/briefing/record
```

Required permission: `ATLAS_RECORD`.

Available to:

- `REVIEWER`;
- `ORG_ADMIN`;
- `SYSTEM_ADMIN`.

The endpoint builds the same package and records:

- one `ORBYN_ATLAS_BRIEFING` output in `REVIEW` state;
- one `Orbyn Atlas Briefing Proof Receipt` evidence reference.

A case owner cannot record their own final briefing evidence, including an owner who also holds an administrative role.

## Request structure

### Case context

The request declares:

- title;
- operational problem;
- sector;
- country;
- analysis horizon;
- optional asset description.

The API derives the Kernel case ID, organization ID, and owner ID from authenticated state.

### Sources

Each source has a stable UUID, title, type, confidence from 0 to 100, sensitivity, optional URI, and notes.

Supported source types are:

- `PUBLIC`;
- `MANUAL`;
- `INTERNAL_APPROVED`;
- `SYNTHETIC`.

A source cannot be more sensitive than its Kernel case.

### Signals and risks

Signals reference one or more declared source UUIDs. Risks reference one or more declared signal UUIDs.

Risk severity is deterministic:

```text
probability × impact
```

Both values use a scale from 1 to 5.

A critical risk automatically generates a recommendation to escalate to Aegis before any deployment.

### Stakeholders

Stakeholders include name, role, influence, exposure, and interests. Influence and exposure use a scale from 1 to 5.

### Scenarios

Every briefing requires exactly one of each:

- `BASE`;
- `ADVERSE`;
- `OPTIMISTIC`;
- `STRESS`.

Each scenario requires:

- narrative;
- assumptions;
- early indicators;
- response options.

## Epistemic separation

Atlas keeps four statement classes separate:

- `FACT`, which requires source references;
- `INFERENCE`, derived from risk calculations;
- `ASSUMPTION`, derived from scenarios;
- `RECOMMENDATION`, proposed for human review.

The API does not silently convert assumptions or inferences into facts.

## Determinism and traceability

Every source, signal, risk, stakeholder, and scenario carries a stable caller-provided UUID. Those identifiers allow references to be validated and make the same structured input produce the same fingerprint.

Generated briefing and receipt IDs remain unique per build. The input fingerprint remains stable for equivalent input.

## Separation of duties

- `CASE_OWNER` may build but cannot record the final briefing.
- `REVIEWER` may build and record but cannot create the original case.
- Recording a briefing does not constitute Kernel approval.
- A briefing does not create Aegis Clearance.
- A briefing does not create Vigilance permissions.
- No endpoint changes a case to `ACTIVE`.

## Validation

The API rejects:

- missing collections;
- duplicate entity IDs;
- broken source or signal references;
- source sensitivity above case sensitivity;
- incomplete or duplicated scenario sets;
- invalid confidence, probability, impact, influence, or exposure values;
- cross-organization access;
- owner attempts to record final evidence.

## Explicit limits

Version 0.5 does not:

- collect public or private data automatically;
- connect to ports, logistics platforms, utilities, or critical systems;
- predict real-world outcomes with guaranteed accuracy;
- execute response options;
- control infrastructure;
- run Aegis or ARIA automatically;
- certify compliance;
- replace a named human decision-maker.

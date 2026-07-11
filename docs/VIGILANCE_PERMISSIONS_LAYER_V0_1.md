# Vigilance Permissions Layer v0.1

## Purpose

Vigilance converts an approved agent blueprint into an explicit, least-privilege permission boundary. It separates reading, writing, sending, deleting, and executing, and records every grant, review, approval, authorization decision, emergency stop, and revocation without destructive history changes.

Vigilance does **not** create credentials, execute tools, deploy agents, or replace the accountable human owner.

## Permission lifecycle

```text
DRAFT
→ named human activation
→ ACTIVE
→ action authorization
→ optional approval request
→ ALLOWED / DENIED / PENDING_APPROVAL
→ action evidence recorded
→ review, revision, suspension, emergency disable, or revocation
```

Every revision creates a new immutable version. Previous approvals and authorization receipts remain preserved but cannot authorize a newer permission fingerprint.

## Explicit action classes

- `READ`
- `WRITE`
- `SEND`
- `DELETE`
- `EXECUTE`

`SEND`, `DELETE`, and `EXECUTE` always require a named human approval. Additional actions, including `WRITE`, may also be configured as approval-gated.

## Minimum grant contents

A permission grant must identify:

- Kernel case;
- exact OAAA blueprint, version, and safety fingerprint;
- agent or service subject;
- accountable owner;
- tool name;
- explicit resource prefixes;
- allowed and denied action classes;
- actions requiring approval;
- sensitivity;
- business reason;
- review date;
- expiry date.

Wildcards are forbidden. A resource outside an explicit prefix is denied.

## Separation of duties

- The permission subject cannot create, activate, revise, suspend, or revoke its own grant.
- The permission subject may request an approval for an exact action and resource.
- The requester cannot approve its own request.
- ORANGE and RED grants require separation between the grant owner and activation approver.

## Authorization outcomes

- `ALLOWED`: the exact action and resource are within the active grant and any required approval exists.
- `DENIED`: the action, resource, identity, state, review, expiry, or human decision blocks the operation.
- `PENDING_APPROVAL`: the action is allowed in principle but needs a named human decision.
- `EMERGENCY_BLOCK`: an emergency disable state blocks all actions immediately.

An authorization receipt is evidence of a decision. It is not the execution itself.

## Emergency control

A named human can emergency-disable a grant. This creates a new `SUSPENDED` version, records the reason, and causes every subsequent authorization to return `EMERGENCY_BLOCK`.

Revocation is permanent for that grant lineage. Reactivation requires a new governed grant or a separately reviewed design.

## Evidence

Vigilance records:

- permission versions;
- permission and integrity fingerprints;
- activation receipts;
- approval requests and decisions;
- authorization receipts;
- action evidence references;
- emergency and revocation events.

Kernel receives mirrored outputs and evidence URIs using the `vigilance://` namespace.

## Boundaries

Version 0.1:

- uses an in-memory development repository;
- does not issue OAuth tokens, API keys, or passwords;
- does not call external tools;
- does not operate critical infrastructure;
- does not claim legal or regulatory certification;
- must be migrated to durable persistence and authenticated identities before a pilot.

"""Acceptance tests for a local Vigilance receipt-binding candidate.

All grants, actors, resources and execution references are synthetic.
Recording an event is not an execution of a tool or an external action.
"""

from dataclasses import replace
from uuid import uuid4

import pytest
from test_vigilance import activate, build_system, create_draft

from astrynn_devforge.vigilance import (
    AuthorizationOutcome,
    PermissionAction,
    PermissionBoundaryError,
    StalePermissionError,
)


@pytest.fixture
def rig():
    service, _kernel, repository, case, owner = build_system()
    subject = uuid4()
    grant = create_draft(service, case, owner, subject_id=subject)
    active, _ = activate(service, grant, owner)

    def authorize(action):
        return service.authorize_action(
            grant_id=active.grant_id,
            subject_id=subject,
            action=action,
            resource="gmail://threads/approved/synthetic",
            evaluated_by=owner,
        )

    return service, repository, active, owner, authorize


def record(service, owner, receipt):
    return service.record_action_execution(
        authorization=receipt,
        recorded_by=owner,
        execution_reference="synthetic://never-executed",
    )


def test_unstored_allowed_receipt_is_rejected(rig):
    service, repository, active, owner, authorize = rig
    denied = authorize(PermissionAction.DELETE)
    forged = replace(denied, id=uuid4(), outcome=AuthorizationOutcome.ALLOWED)
    assert all(
        item.id != forged.id
        for item in repository.authorization_receipts_for_grant(active.grant_id)
    )
    before = len(repository.events_for_grant(active.grant_id))
    with pytest.raises(PermissionBoundaryError):
        record(service, owner, forged)
    assert len(repository.events_for_grant(active.grant_id)) == before


def test_changed_denial_with_same_id_is_rejected(rig):
    service, repository, active, owner, authorize = rig
    denied = authorize(PermissionAction.DELETE)
    forged = replace(denied, outcome=AuthorizationOutcome.ALLOWED)
    before = len(repository.events_for_grant(active.grant_id))
    with pytest.raises(PermissionBoundaryError):
        record(service, owner, forged)
    assert len(repository.events_for_grant(active.grant_id)) == before


def test_changed_resource_on_stored_allowed_receipt_is_rejected(rig):
    service, repository, active, owner, authorize = rig
    allowed = authorize(PermissionAction.READ)
    forged = replace(allowed, resource="gmail://threads/approved/other")
    before = len(repository.events_for_grant(active.grant_id))
    with pytest.raises(PermissionBoundaryError):
        record(service, owner, forged)
    assert len(repository.events_for_grant(active.grant_id)) == before


def test_duplicate_stored_receipt_id_is_rejected(rig, monkeypatch):
    service, repository, active, owner, authorize = rig
    allowed = authorize(PermissionAction.READ)
    before = len(repository.events_for_grant(active.grant_id))
    monkeypatch.setattr(
        repository, "authorization_receipts_for_grant", lambda _id: (allowed, allowed)
    )
    with pytest.raises(PermissionBoundaryError):
        record(service, owner, allowed)
    assert len(repository.events_for_grant(active.grant_id)) == before


def test_exact_stored_allowed_receipt_still_records_event(rig):
    service, _repository, _active, owner, authorize = rig
    allowed = authorize(PermissionAction.READ)
    event = record(service, owner, allowed)
    assert event.details["authorization_receipt_id"] == str(allowed.id)


def test_revoked_grant_rejects_previously_stored_receipt(rig):
    service, _repository, active, owner, authorize = rig
    allowed = authorize(PermissionAction.READ)
    service.revoke_grant(grant_id=active.grant_id, revoked_by=owner, reason="Synthetic")
    with pytest.raises(StalePermissionError):
        record(service, owner, allowed)


def test_receipt_store_failure_does_not_record_execution(rig, monkeypatch):
    service, repository, active, owner, authorize = rig
    allowed = authorize(PermissionAction.READ)
    before = len(repository.events_for_grant(active.grant_id))

    def fail_store(_grant_id):
        raise RuntimeError("synthetic receipt store failure")

    monkeypatch.setattr(repository, "authorization_receipts_for_grant", fail_store)
    with pytest.raises(RuntimeError, match="receipt store failure"):
        record(service, owner, allowed)
    assert len(repository.events_for_grant(active.grant_id)) == before

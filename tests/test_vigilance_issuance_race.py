"""Synthetic in-process tests for grant changes during receipt issuance."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import timedelta
from threading import Barrier, Event
from uuid import uuid4

import pytest
from test_vigilance import activate, build_system, create_draft

import astrynn_devforge.vigilance.repository as vigilance_repository
from astrynn_devforge.vigilance import (
    AuthorizationOutcome,
    DuplicatePermissionVersionError,
    GrantStatus,
    PermissionAction,
    PermissionEventType,
    StalePermissionError,
    VigilancePermissionService,
)


@pytest.mark.parametrize("change", ["revoke", "disable"])
def test_changed_grant_cannot_receive_stale_authorization(monkeypatch, change):
    issuer, kernel, repository, case, owner = build_system()
    mutator = VigilancePermissionService(kernel, repository)
    subject = uuid4()
    grant = create_draft(issuer, case, owner, subject_id=subject)
    active, _ = activate(issuer, grant, owner)
    evaluated, proceed = Event(), Event()
    evaluate = issuer._evaluate

    def pause_after_evaluation(**kwargs):
        result = evaluate(**kwargs)
        evaluated.set()
        if not proceed.wait(timeout=5):
            raise TimeoutError("synthetic race timed out")
        return result

    monkeypatch.setattr(issuer, "_evaluate", pause_after_evaluation)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(
            issuer.authorize_action,
            grant_id=active.grant_id,
            subject_id=subject,
            action=PermissionAction.READ,
            resource="gmail://threads/approved/synthetic",
            evaluated_by=owner,
        )
        try:
            assert evaluated.wait(timeout=5)
            if change == "revoke":
                mutator.revoke_grant(
                    grant_id=active.grant_id, revoked_by=owner, reason="Synthetic"
                )
            else:
                mutator.emergency_disable(
                    grant_id=active.grant_id, disabled_by=owner, reason="Synthetic"
                )
        finally:
            proceed.set()
        with pytest.raises(StalePermissionError):
            future.result(timeout=5)
    assert repository.authorization_receipts_for_grant(active.grant_id) == ()
    assert all(
        event.event_type is not PermissionEventType.AUTHORIZATION_EVALUATED
        for event in repository.events_for_grant(active.grant_id)
    )
    assert all(
        not evidence.label.startswith("Vigilance authorization")
        for evidence in kernel.evidence_for_case(case.id)
    )


def test_unchanged_grant_still_records_allowed_and_denied_receipts():
    service, _kernel, repository, case, owner = build_system()
    subject = uuid4()
    grant = create_draft(service, case, owner, subject_id=subject)
    active, _ = activate(service, grant, owner)
    receipts = [
        service.authorize_action(
            grant_id=active.grant_id,
            subject_id=subject,
            action=action,
            resource="gmail://threads/approved/synthetic",
            evaluated_by=owner,
        )
        for action in (PermissionAction.READ, PermissionAction.DELETE)
    ]
    assert [item.outcome for item in receipts] == [
        AuthorizationOutcome.ALLOWED,
        AuthorizationOutcome.DENIED,
    ]
    assert repository.authorization_receipts_for_grant(active.grant_id) == tuple(receipts)


@pytest.mark.parametrize("deadline", ["review_at", "expires_at"])
def test_allowed_receipt_not_stored_after_grant_deadline(monkeypatch, deadline):
    service, kernel, repository, case, owner = build_system()
    subject = uuid4()
    grant = create_draft(service, case, owner, subject_id=subject)
    active, _ = activate(service, grant, owner)
    prior_events = repository.events_for_grant(active.grant_id)
    prior_evidence = kernel.evidence_for_case(case.id)
    after_deadline = getattr(active, deadline) + timedelta(microseconds=1)
    monkeypatch.setattr(vigilance_repository, "utc_now", lambda: after_deadline, raising=False)

    with pytest.raises(StalePermissionError):
        service.authorize_action(
            grant_id=active.grant_id,
            subject_id=subject,
            action=PermissionAction.READ,
            resource="gmail://threads/approved/synthetic",
            evaluated_by=owner,
        )
    assert repository.authorization_receipts_for_grant(active.grant_id) == ()
    assert repository.events_for_grant(active.grant_id) == prior_events
    assert kernel.evidence_for_case(case.id) == prior_evidence


def test_receipt_store_failure_leaves_no_authorization_evidence(monkeypatch):
    service, kernel, repository, case, owner = build_system()
    subject = uuid4()
    grant = create_draft(service, case, owner, subject_id=subject)
    active, _ = activate(service, grant, owner)
    prior_events = repository.events_for_grant(active.grant_id)
    prior_evidence = kernel.evidence_for_case(case.id)

    def fail_before_insert(_receipt):
        raise RuntimeError("synthetic issuance store failure")

    monkeypatch.setattr(repository, "_append_authorization_receipt_unlocked", fail_before_insert)
    with pytest.raises(RuntimeError, match="issuance store failure"):
        service.authorize_action(
            grant_id=active.grant_id,
            subject_id=subject,
            action=PermissionAction.READ,
            resource="gmail://threads/approved/synthetic",
            evaluated_by=owner,
        )
    assert repository.authorization_receipts_for_grant(active.grant_id) == ()
    assert repository.events_for_grant(active.grant_id) == prior_events
    assert kernel.evidence_for_case(case.id) == prior_evidence


def test_two_writers_cannot_append_the_same_next_grant_version():
    service, _kernel, repository, case, owner = build_system()
    grant = create_draft(service, case, owner)
    active, _ = activate(service, grant, owner)
    contenders = [
        replace(
            active,
            id=uuid4(),
            version=active.version + 1,
            parent_version_id=active.id,
            status=GrantStatus.REVOKED,
            approved_by=None,
            activated_at=None,
            reason="Synthetic competing version",
        )
        for _ in range(2)
    ]
    barrier = Barrier(2)

    def append(version):
        barrier.wait(timeout=5)
        try:
            repository.append_version(version)
            return "committed"
        except DuplicatePermissionVersionError:
            return "stale"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(append, contenders))
    assert sorted(outcomes) == ["committed", "stale"]
    assert repository.latest_version(active.grant_id).version == active.version + 1

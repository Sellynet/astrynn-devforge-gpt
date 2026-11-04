"""Synthetic in-process race between a grant change and recording an action."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from threading import Event, get_ident
from uuid import uuid4

import pytest
from test_vigilance import activate, build_system, create_draft

from astrynn_devforge.vigilance import (
    AuthorizationOutcome,
    PermissionAction,
    PermissionBoundaryError,
    PermissionEventType,
    StalePermissionError,
    VigilancePermissionService,
)


@pytest.mark.parametrize("change", ["revoke", "disable"])
def test_change_during_recording_does_not_append_stale_event(monkeypatch, change):
    recorder, kernel, repository, case, owner = build_system()
    mutator = VigilancePermissionService(kernel, repository)
    subject = uuid4()
    grant = create_draft(recorder, case, owner, subject_id=subject)
    active, _ = activate(recorder, grant, owner)
    receipt = recorder.authorize_action(
        grant_id=active.grant_id,
        subject_id=subject,
        action=PermissionAction.READ,
        resource="gmail://threads/approved/synthetic",
        evaluated_by=owner,
    )
    original_latest = repository.latest_version
    observed, proceed = Event(), Event()
    main_thread = get_ident()

    def pause_recording(grant_id):
        snapshot = original_latest(grant_id)
        if get_ident() != main_thread:
            observed.set()
            if not proceed.wait(timeout=5):
                raise TimeoutError("synthetic recording race timed out")
        return snapshot

    monkeypatch.setattr(repository, "latest_version", pause_recording)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(
            recorder.record_action_execution,
            authorization=receipt,
            recorded_by=owner,
            execution_reference="synthetic://never-executed",
        )
        try:
            assert observed.wait(timeout=5)
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
    assert all(
        event.event_type is not PermissionEventType.ACTION_RECORDED
        for event in repository.events_for_grant(active.grant_id)
    )


def test_receipt_removed_after_precheck_cannot_record_event(monkeypatch):
    service, _kernel, repository, case, owner = build_system()
    subject = uuid4()
    grant = create_draft(service, case, owner, subject_id=subject)
    active, _ = activate(service, grant, owner)
    receipt = service.authorize_action(
        grant_id=active.grant_id,
        subject_id=subject,
        action=PermissionAction.READ,
        resource="gmail://threads/approved/synthetic",
        evaluated_by=owner,
    )
    original_read = repository.authorization_receipts_for_grant

    def disappear_after_read(grant_id):
        snapshot = original_read(grant_id)
        # Synthetic corruption between the service's precheck and the atomic write.
        with repository._grant_receipt_lock:
            repository._authorization_receipts.clear()
        return snapshot

    monkeypatch.setattr(repository, "authorization_receipts_for_grant", disappear_after_read)
    with pytest.raises(PermissionBoundaryError):
        service.record_action_execution(
            authorization=receipt,
            recorded_by=owner,
            execution_reference="synthetic://never-executed",
        )
    assert all(
        event.event_type is not PermissionEventType.ACTION_RECORDED
        for event in repository.events_for_grant(active.grant_id)
    )


def test_action_event_store_failure_does_not_append_event(monkeypatch):
    service, _kernel, repository, case, owner = build_system()
    subject = uuid4()
    grant = create_draft(service, case, owner, subject_id=subject)
    active, _ = activate(service, grant, owner)
    receipt = service.authorize_action(
        grant_id=active.grant_id,
        subject_id=subject,
        action=PermissionAction.READ,
        resource="gmail://threads/approved/synthetic",
        evaluated_by=owner,
    )
    before = repository.events_for_grant(active.grant_id)

    def fail_before_append(_event):
        raise RuntimeError("synthetic event store failure")

    monkeypatch.setattr(repository, "_append_event_unlocked", fail_before_append)
    with pytest.raises(RuntimeError, match="event store failure"):
        service.record_action_execution(
            authorization=receipt,
            recorded_by=owner,
            execution_reference="synthetic://never-executed",
        )
    assert repository.events_for_grant(active.grant_id) == before


def test_receipt_without_evaluation_event_cannot_record_action(monkeypatch):
    service, kernel, repository, case, owner = build_system()
    subject = uuid4()
    grant = create_draft(service, case, owner, subject_id=subject)
    active, _ = activate(service, grant, owner)
    append_evidence = kernel.append_evidence

    def fail_authorization_evidence(evidence):
        if evidence.label.startswith("Vigilance authorization"):
            raise RuntimeError("synthetic evidence failure")
        return append_evidence(evidence)

    monkeypatch.setattr(kernel, "append_evidence", fail_authorization_evidence)
    with pytest.raises(RuntimeError, match="synthetic evidence failure"):
        service.authorize_action(
            grant_id=active.grant_id,
            subject_id=subject,
            action=PermissionAction.READ,
            resource="gmail://threads/approved/synthetic",
            evaluated_by=owner,
        )
    receipt, = repository.authorization_receipts_for_grant(active.grant_id)
    assert receipt.outcome is AuthorizationOutcome.ALLOWED
    with pytest.raises(PermissionBoundaryError):
        service.record_action_execution(
            authorization=receipt,
            recorded_by=owner,
            execution_reference="synthetic://never-executed",
        )
    assert all(
        event.event_type is not PermissionEventType.ACTION_RECORDED
        for event in repository.events_for_grant(active.grant_id)
    )


@pytest.mark.parametrize("corruption", ["outcome", "action", "resource", "actor", "duplicate"])
def test_inconsistent_evaluation_event_cannot_record_action(corruption):
    service, _kernel, repository, case, owner = build_system()
    subject = uuid4()
    grant = create_draft(service, case, owner, subject_id=subject)
    active, _ = activate(service, grant, owner)
    receipt = service.authorize_action(
        grant_id=active.grant_id,
        subject_id=subject,
        action=PermissionAction.READ,
        resource="gmail://threads/approved/synthetic",
        evaluated_by=owner,
    )
    with repository._grant_receipt_lock:
        index = next(
            n for n, event in enumerate(repository._events)
            if event.event_type is PermissionEventType.AUTHORIZATION_EVALUATED
        )
        event = repository._events[index]
        if corruption == "duplicate":
            repository._events.append(replace(event, id=uuid4()))
        elif corruption == "actor":
            repository._events[index] = replace(event, actor_id=uuid4())
        else:
            details = dict(event.details)
            details[corruption] = "synthetic mismatch"
            repository._events[index] = replace(event, details=details)
    with pytest.raises(PermissionBoundaryError):
        service.record_action_execution(
            authorization=receipt,
            recorded_by=owner,
            execution_reference="synthetic://never-executed",
        )
    assert all(
        event.event_type is not PermissionEventType.ACTION_RECORDED
        for event in repository.events_for_grant(active.grant_id)
    )

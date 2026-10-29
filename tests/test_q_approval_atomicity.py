"""Atomic approval/event acceptance tests for the isolated Q correction candidate."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from sqlalchemy import event
from sqlalchemy.exc import OperationalError

from astrynn_devforge.kernel import (
    ApprovalDecision, ApprovalRecord, ApprovalRequiredError, CaseEvent, CaseStatus,
    InMemoryKernelRepository, KernelService, Sensitivity,
)
from astrynn_devforge.persistence.sqlalchemy_kernel import SQLAlchemyKernelRepository, StaleCaseWriteError


@pytest.fixture
def rig(tmp_path):
    url = f"sqlite:///{tmp_path / 'approval.db'}"
    repo = SQLAlchemyKernelRepository(url, create_schema=True)
    owner, approver = uuid4(), uuid4()
    service = KernelService(repo)
    case = service.create_case(title="Approval", description="fixture", owner_id=owner,
        organization_id=uuid4(), sensitivity=Sensitivity.ORANGE, actor_id=owner)
    service.transition_case(case_id=case.id, target=CaseStatus.IN_REVIEW,
                            actor_id=owner, reason="fixture review")
    yield repo, service, case.id, owner, approver, url
    repo.close()


def record(service, case_id, approver, decision=ApprovalDecision.APPROVE, conditions=()):
    return service.record_approval(case_id=case_id, approver_id=approver, decision=decision,
                                   rationale="fixture approval", conditions=conditions)


def test_success_persists_approval_and_matching_event_after_restart(rig):
    repo, service, case_id, owner, approver, url = rig
    approval = record(service, case_id, approver)
    repo.close()
    reopened = SQLAlchemyKernelRepository(url)
    assert reopened.approvals_for_case(case_id)[-1].id == approval.id
    events = [x for x in reopened.get_case(case_id).events if x.event_type == "APPROVAL_RECORDED"]
    assert len(events) == 1 and events[0].details["approval_id"] == str(approval.id)
    assert KernelService(reopened).transition_case(case_id=case_id, target=CaseStatus.APPROVED,
        actor_id=owner, reason="approved").status is CaseStatus.APPROVED
    reopened.close()


def test_competing_case_update_rejects_and_leaves_no_approval(rig, monkeypatch):
    repo, service, case_id, owner, approver, url = rig
    other = SQLAlchemyKernelRepository(url)
    original = repo.commit_approval_and_case
    def interleave(approval, case):
        fresh = other.get_case(case_id)
        fresh.record_event(CaseEvent(event_type="COMPETING_WRITE_TEST_ONLY", actor_id=owner, details={}))
        other.save_case(fresh)
        return original(approval, case)
    monkeypatch.setattr(repo, "commit_approval_and_case", interleave)
    with pytest.raises(StaleCaseWriteError):
        record(service, case_id, approver)
    assert repo.approvals_for_case(case_id) == ()
    assert not any(x.event_type == "APPROVAL_RECORDED" for x in repo.get_case(case_id).events)
    with pytest.raises(ApprovalRequiredError):
        service.transition_case(case_id=case_id, target=CaseStatus.APPROVED,
                                actor_id=owner, reason="no approval")
    other.close()


def test_failure_after_flush_rolls_back_approval_and_case_event(rig):
    repo, service, case_id, _, approver, url = rig
    before = repo.get_case(case_id)
    def fail(*_):
        raise RuntimeError("injected failure after flush")
    event.listen(repo._sessions, "after_flush", fail)
    try:
        with pytest.raises(RuntimeError, match="injected"):
            record(service, case_id, approver)
    finally:
        event.remove(repo._sessions, "after_flush", fail)
    repo.close()
    reopened = SQLAlchemyKernelRepository(url)
    after = reopened.get_case(case_id)
    assert reopened.approvals_for_case(case_id) == ()
    assert after.version == before.version
    assert [x.id for x in after.events] == [x.id for x in before.events]
    reopened.close()


def test_legacy_orphan_approval_is_not_eligible_for_governance(rig):
    repo, service, case_id, owner, approver, _ = rig
    repo.append_approval(ApprovalRecord(case_id=case_id, approver_id=approver,
        decision=ApprovalDecision.APPROVE, rationale="unlinked fixture"))
    with pytest.raises(ApprovalRequiredError, match="matching case event"):
        service.transition_case(case_id=case_id, target=CaseStatus.APPROVED,
                                actor_id=owner, reason="must fail closed")
    assert repo.get_case(case_id).status is CaseStatus.IN_REVIEW


def test_event_with_wrong_actor_does_not_validate_legacy_approval(rig):
    repo, service, case_id, owner, approver, _ = rig
    approval = ApprovalRecord(case_id=case_id, approver_id=approver,
                              decision=ApprovalDecision.APPROVE, rationale="fixture")
    repo.append_approval(approval)
    snapshot = repo.get_case(case_id)
    snapshot.record_event(CaseEvent(event_type="APPROVAL_RECORDED", actor_id=owner,
        details={"approval_id": str(approval.id), "decision": approval.decision.value, "conditions": []}))
    repo.save_case(snapshot)
    with pytest.raises(ApprovalRequiredError, match="matching case event"):
        service.transition_case(case_id=case_id, target=CaseStatus.APPROVED,
                                actor_id=owner, reason="mismatched event")


def test_conditional_approval_remains_on_hold_after_linked_event(rig):
    repo, service, case_id, owner, approver, _ = rig
    record(service, case_id, approver, ApprovalDecision.APPROVE_WITH_CONDITIONS, ("verify control",))
    service.transition_case(case_id=case_id, target=CaseStatus.APPROVED, actor_id=owner, reason="review")
    with pytest.raises(ApprovalRequiredError, match="authoritative verification"):
        service.transition_case(case_id=case_id, target=CaseStatus.ACTIVE, actor_id=owner, reason="hold")
    assert repo.get_case(case_id).status is CaseStatus.APPROVED


def test_duplicate_approval_id_is_rejected_without_extra_event(rig):
    repo, _, case_id, _, approver, _ = rig
    approval = ApprovalRecord(case_id=case_id, approver_id=approver,
                              decision=ApprovalDecision.APPROVE, rationale="fixture")
    snapshot = repo.get_case(case_id)
    snapshot.record_event(CaseEvent(event_type="APPROVAL_RECORDED", actor_id=approver,
        details={"approval_id": str(approval.id), "decision": approval.decision.value, "conditions": []}))
    repo.commit_approval_and_case(approval, snapshot)
    with pytest.raises(ValueError, match="already exists"):
        repo.commit_approval_and_case(approval, snapshot)
    assert len(repo.approvals_for_case(case_id)) == 1
    assert len([x for x in repo.get_case(case_id).events if x.event_type == "APPROVAL_RECORDED"]) == 1


@pytest.mark.parametrize("attempt_number", range(5))
def test_simultaneous_approvals_leave_only_one_linked_commit(rig, monkeypatch, attempt_number):
    repo, _, case_id, _, approver, url = rig
    other = SQLAlchemyKernelRepository(url)
    first, second = repo.commit_approval_and_case, other.commit_approval_and_case
    barrier = Barrier(2)
    def wrap(operation):
        def commit(approval, case):
            barrier.wait(timeout=5)
            return operation(approval, case)
        return commit
    monkeypatch.setattr(repo, "commit_approval_and_case", wrap(first))
    monkeypatch.setattr(other, "commit_approval_and_case", wrap(second))
    def attempt(repository):
        try:
            record(KernelService(repository), case_id, approver)
            return "committed"
        except (StaleCaseWriteError, OperationalError) as exc:
            return type(exc).__name__
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(attempt, (repo, other)))
    assert outcomes.count("committed") == 1, outcomes
    approvals = repo.approvals_for_case(case_id)
    approval_events = [x for x in repo.get_case(case_id).events if x.event_type == "APPROVAL_RECORDED"]
    assert len(approvals) == len(approval_events) == 1
    assert approval_events[0].details["approval_id"] == str(approvals[0].id)
    other.close()


def test_in_memory_legacy_orphan_fails_closed():
    repo = InMemoryKernelRepository()
    service = KernelService(repo)
    owner, approver = uuid4(), uuid4()
    case = service.create_case(title="Memory", description="fixture", owner_id=owner,
        organization_id=uuid4(), sensitivity=Sensitivity.ORANGE, actor_id=owner)
    service.transition_case(case_id=case.id, target=CaseStatus.IN_REVIEW, actor_id=owner, reason="review")
    repo.append_approval(ApprovalRecord(case_id=case.id, approver_id=approver,
        decision=ApprovalDecision.APPROVE, rationale="unlinked fixture"))
    with pytest.raises(ApprovalRequiredError, match="matching case event"):
        service.transition_case(case_id=case.id, target=CaseStatus.APPROVED, actor_id=owner, reason="block")

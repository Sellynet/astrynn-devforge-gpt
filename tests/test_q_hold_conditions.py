"""Negative acceptance tests for exact historical Kernel, source-aligned patch.

Tests operate on governance CaseStatus only. Synthetic events never count as
canonical authority facts. XFAIL tests explicitly name capabilities NOT built.
"""
from uuid import uuid4

import pytest

from astrynn_devforge.kernel import (
    ApprovalDecision, ApprovalRequiredError, CaseEvent, CaseStatus,
    EvidenceReference, InMemoryKernelRepository, KernelService, Sensitivity,
)

CONDITION = "Evidence of control completion required before governance activation"


def fixture(*, decision=ApprovalDecision.APPROVE_WITH_CONDITIONS,
            sensitivity=Sensitivity.ORANGE):
    repo = InMemoryKernelRepository()
    svc = KernelService(repo)
    owner, issuer = uuid4(), uuid4()
    case = svc.create_case(
        title="Offline policy boundary case", description="test only", owner_id=owner,
        organization_id=uuid4(), sensitivity=sensitivity, actor_id=owner,
    )
    svc.transition_case(case_id=case.id, target=CaseStatus.IN_REVIEW,
                        actor_id=owner, reason="Review")
    svc.record_approval(case_id=case.id, approver_id=issuer, decision=decision,
                        rationale="Fixture: governance only",
                        conditions=(CONDITION,) if decision == ApprovalDecision.APPROVE_WITH_CONDITIONS else ())
    return svc, repo, case.id, owner, issuer


def approved(svc, case_id, owner):
    return svc.transition_case(case_id=case_id, target=CaseStatus.APPROVED,
                               actor_id=owner, reason="Approve governance state")


def activate(svc, case_id, owner):
    return svc.transition_case(case_id=case_id, target=CaseStatus.ACTIVE,
                               actor_id=owner, reason="Proposed governance activation")


def assert_held_cleanly(svc, repo, case_id, owner):
    before = repo.get_case(case_id)
    before_approvals = repo.approvals_for_case(case_id)
    with pytest.raises(ApprovalRequiredError, match="authoritative verification"):
        activate(svc, case_id, owner)
    after = repo.get_case(case_id)
    assert (after.status, after.version, len(after.events)) == (
        before.status, before.version, len(before.events)
    )
    assert repo.approvals_for_case(case_id) == before_approvals


def test_01_conditional_can_enter_approved_for_review_without_promotion():
    svc, repo, case, owner, issuer = fixture()
    assert approved(svc, case, owner).status is CaseStatus.APPROVED
    assert repo.approvals_for_case(case)[-1].conditions == (CONDITION,)


def test_02_condition_without_verified_receipt_blocks_active():
    svc, repo, case, owner, issuer = fixture()
    approved(svc, case, owner)
    assert_held_cleanly(svc, repo, case, owner)


def test_03_unconditional_approval_still_activates():
    svc, repo, case, owner, issuer = fixture(decision=ApprovalDecision.APPROVE)
    approved(svc, case, owner)
    assert activate(svc, case, owner).status is CaseStatus.ACTIVE


def test_04_spoofed_evidence_ref_does_not_unlock_condition():
    svc, repo, case, owner, issuer = fixture()
    approved(svc, case, owner)
    repo.append_evidence(EvidenceReference(
        case_id=case, label="all checks passed", uri="test://not-authenticated",
        sensitivity=Sensitivity.ORANGE,
    ))
    assert_held_cleanly(svc, repo, case, owner)


def test_05_spoofed_event_does_not_unlock_condition():
    svc, repo, case, owner, issuer = fixture()
    approved(svc, case, owner)
    snapshot = repo.get_case(case)
    snapshot.record_event(CaseEvent(
        event_type="CONDITIONS_VERIFIED_TEST_ONLY", actor_id=owner,
        details={"trusted": True, "source": "unverified user text"},
    ))
    repo.save_case(snapshot)
    assert_held_cleanly(svc, repo, case, owner)


def test_06_conditional_other_sensitivity_also_held():
    svc, repo, case, owner, issuer = fixture(sensitivity=Sensitivity.GREEN)
    approved(svc, case, owner)
    assert_held_cleanly(svc, repo, case, owner)


def test_07_latest_reject_prevents_approved():
    svc, repo, case, owner, issuer = fixture(decision=ApprovalDecision.REJECT)
    with pytest.raises(ApprovalRequiredError, match="blocks APPROVED"):
        approved(svc, case, owner)


def test_08_latest_unconditioned_requires_actual_approval_record():
    repo = InMemoryKernelRepository()
    svc = KernelService(repo)
    owner = uuid4()
    case = svc.create_case(title="Unapproved", description="test", owner_id=owner,
                           organization_id=uuid4(), sensitivity=Sensitivity.ORANGE,
                           actor_id=owner)
    svc.transition_case(case_id=case.id, target=CaseStatus.IN_REVIEW,
                        actor_id=owner, reason="review")
    with pytest.raises(ApprovalRequiredError, match="Approval required"):
        approved(svc, case.id, owner)


def test_09_conditional_failed_active_has_no_new_status_event():
    svc, repo, case, owner, issuer = fixture()
    approved(svc, case, owner)
    before = len(repo.get_case(case).events)
    with pytest.raises(ApprovalRequiredError):
        activate(svc, case, owner)
    assert len(repo.get_case(case).events) == before


def test_10_separation_of_duties_still_works():
    svc, repo, case, owner, issuer = fixture()
    with pytest.raises(ApprovalRequiredError, match="separation"):
        svc.record_approval(case_id=case, approver_id=owner,
                            decision=ApprovalDecision.APPROVE,
                            rationale="Bad self approval")


def test_11_explicit_condition_remains_in_original_approval_record():
    svc, repo, case, owner, issuer = fixture()
    approved(svc, case, owner)
    before = repo.approvals_for_case(case)[-1]
    assert_held_cleanly(svc, repo, case, owner)
    assert repo.approvals_for_case(case)[-1] == before


def test_12_no_new_execution_or_grant_api_introduced():
    svc, repo, case, owner, issuer = fixture()
    assert not hasattr(svc, "issue_token")
    assert not hasattr(svc, "execute_action")
    assert not hasattr(svc, "certify_execution")
    approved(svc, case, owner)
    assert_held_cleanly(svc, repo, case, owner)


@pytest.mark.xfail(strict=True, reason="NO canonical issuer revocation fact binding; synthetic events cannot be trusted")
def test_unmet_c02_real_issuer_revocation_fails_closed():
    svc, repo, case, owner, issuer = fixture(decision=ApprovalDecision.APPROVE)
    approved(svc, case, owner)
    snapshot = repo.get_case(case)
    snapshot.record_event(CaseEvent(event_type="ISSUER_REVOKED_TEST_ONLY", actor_id=owner,
                                     details={"issuer": str(issuer)}))
    repo.save_case(snapshot)
    with pytest.raises(ApprovalRequiredError):
        activate(svc, case, owner)


@pytest.mark.xfail(strict=True, reason="NO trusted late evidence semantics in existing Kernel")
def test_unmet_c09_late_material_contradiction_fails_closed():
    svc, repo, case, owner, issuer = fixture(decision=ApprovalDecision.APPROVE)
    approved(svc, case, owner)
    repo.append_evidence(EvidenceReference(case_id=case, label="LATE_CONTRADICTION_TEST_ONLY",
                                           uri="test://untrusted/1", sensitivity=Sensitivity.ORANGE))
    with pytest.raises(ApprovalRequiredError):
        activate(svc, case, owner)


@pytest.mark.xfail(strict=True, reason="NO authoritative expiry and at-action policy binding")
def test_unmet_c01_expired_grant_fails_closed():
    svc, repo, case, owner, issuer = fixture(decision=ApprovalDecision.APPROVE)
    approved(svc, case, owner)
    snap = repo.get_case(case)
    snap.record_event(CaseEvent(event_type="GRANT_EXPIRED_TEST_ONLY", actor_id=owner,
                                details={"issuer": str(issuer)}))
    repo.save_case(snap)
    with pytest.raises(ApprovalRequiredError):
        activate(svc, case, owner)

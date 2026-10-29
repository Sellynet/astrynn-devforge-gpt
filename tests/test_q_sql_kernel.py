"""Confrontation 09: real, Git-blob-exact SQLAlchemyKernelRepository and C08 Kernel patch.

All tests use SQLite in a temporary local directory; no Machine SSOT, Mirror,
founder authority or remote action is involved. Assertions about the absence of
institutional policy checks are scope tests, not claims of production bypass.
"""
from __future__ import annotations

from uuid import uuid4

import pytest

from astrynn_devforge.kernel import (
    ApprovalDecision,
    ApprovalRequiredError,
    CaseEvent,
    CaseStatus,
    EvidenceReference,
    KernelService,
    Sensitivity,
)
from astrynn_devforge.persistence.sqlalchemy_kernel import SQLAlchemyKernelRepository, StaleCaseWriteError


def setup_case(tmp_path, *, sensitivity=Sensitivity.ORANGE):
    url = 'sqlite:///' + str(tmp_path / 'isolated_kernel.sqlite3')
    repo = SQLAlchemyKernelRepository(url, create_schema=True)
    svc = KernelService(repo)
    owner, approver, org = uuid4(), uuid4(), uuid4()
    case = svc.create_case(title='Conditional action audit', description='Synthetic test',
                           owner_id=owner, organization_id=org,
                           sensitivity=sensitivity, actor_id=owner)
    svc.transition_case(case_id=case.id, target=CaseStatus.IN_REVIEW,
                        actor_id=owner, reason='Submit review')
    return url, repo, svc, case.id, owner, approver


def condition(svc, case_id, approver):
    return svc.record_approval(case_id=case_id, approver_id=approver,
                               decision=ApprovalDecision.APPROVE_WITH_CONDITIONS,
                               rationale='Requires another verified checkpoint',
                               conditions=('Independent attestation before ACTIVE',))


def activate(svc, case_id, owner):
    return svc.transition_case(case_id=case_id, target=CaseStatus.ACTIVE,
                               actor_id=owner, reason='Attempt activation')


def approve(svc, case_id, owner):
    return svc.transition_case(case_id=case_id, target=CaseStatus.APPROVED,
                               actor_id=owner, reason='Document review')


def test_sql_conditional_can_reach_approved_but_not_active(tmp_path):
    _,repo,svc,cid,owner,reviewer = setup_case(tmp_path)
    condition(svc,cid,reviewer)
    assert approve(svc,cid,owner).status == CaseStatus.APPROVED
    with pytest.raises(ApprovalRequiredError,match='authoritative verification'):
        activate(svc,cid,owner)
    assert repo.get_case(cid).status == CaseStatus.APPROVED
    repo.close()


def test_sql_hold_remains_after_reopen(tmp_path):
    url,repo,svc,cid,owner,reviewer = setup_case(tmp_path)
    condition(svc,cid,reviewer)
    approve(svc,cid,owner)
    before = repo.get_case(cid)
    repo.close()
    repo2 = SQLAlchemyKernelRepository(url,create_schema=False)
    svc2 = KernelService(repo2)
    with pytest.raises(ApprovalRequiredError):
        activate(svc2,cid,owner)
    after = repo2.get_case(cid)
    assert (after.status,after.version,len(after.events)) == (
        before.status,before.version,len(before.events))
    assert repo2.approvals_for_case(cid)[-1].conditions == ('Independent attestation before ACTIVE',)
    repo2.close()


def test_sql_untrusted_evidence_reference_not_activation_attestation(tmp_path):
    _,repo,svc,cid,owner,reviewer = setup_case(tmp_path)
    condition(svc,cid,reviewer)
    approve(svc,cid,owner)
    repo.append_evidence(EvidenceReference(case_id=cid,label='Conditions met',
                                           uri='fixture://unverified',sensitivity=Sensitivity.ORANGE))
    assert repo.evidence_for_case(cid)
    with pytest.raises(ApprovalRequiredError):
        activate(svc,cid,owner)
    assert repo.get_case(cid).status == CaseStatus.APPROVED
    repo.close()


def test_sql_untrusted_case_event_not_activation_attestation(tmp_path):
    _,repo,svc,cid,owner,reviewer = setup_case(tmp_path)
    condition(svc,cid,reviewer)
    approve(svc,cid,owner)
    case=repo.get_case(cid)
    case.record_event(CaseEvent(event_type='CONDITIONS_VERIFIED_TEST_ONLY',actor_id=owner,
                                 details={'claim':'not authenticated'}))
    repo.save_case(case)
    with pytest.raises(ApprovalRequiredError):
        activate(svc,cid,owner)
    assert repo.get_case(cid).status == CaseStatus.APPROVED
    repo.close()


def test_sql_unconditional_approval_reaches_active(tmp_path):
    url,repo,svc,cid,owner,reviewer=setup_case(tmp_path)
    svc.record_approval(case_id=cid,approver_id=reviewer,
        decision=ApprovalDecision.APPROVE,rationale='Unconditional synthetic approval')
    approve(svc,cid,owner)
    assert activate(svc,cid,owner).status == CaseStatus.ACTIVE
    repo.close()
    again=SQLAlchemyKernelRepository(url,create_schema=False)
    assert again.get_case(cid).status == CaseStatus.ACTIVE
    again.close()


def test_sql_latest_rejection_blocks_approval(tmp_path):
    _,repo,svc,cid,owner,reviewer=setup_case(tmp_path)
    svc.record_approval(case_id=cid,approver_id=reviewer,
        decision=ApprovalDecision.REJECT,rationale='Rejected synthetic risk')
    with pytest.raises(ApprovalRequiredError):
        approve(svc,cid,owner)
    assert repo.get_case(cid).status == CaseStatus.IN_REVIEW
    repo.close()


def test_sql_orange_self_approval_still_prohibited(tmp_path):
    _,repo,svc,cid,owner,_=setup_case(tmp_path)
    with pytest.raises(ApprovalRequiredError):
        svc.record_approval(
        case_id=cid,approver_id=owner,decision=ApprovalDecision.APPROVE,rationale='Self')
    assert repo.approvals_for_case(cid) == ()
    repo.close()


def test_sql_idempotent_save_case_no_duplicate_events(tmp_path):
    _,repo,svc,cid,owner,reviewer=setup_case(tmp_path)
    condition(svc,cid,reviewer)
    before=repo.get_case(cid)
    repo.save_case(before)
    after=repo.get_case(cid)
    assert len(after.events)==len(before.events)
    assert after.version==before.version
    repo.close()


def test_sql_conditional_denial_does_not_add_status_event(tmp_path):
    _,repo,svc,cid,owner,reviewer=setup_case(tmp_path)
    condition(svc,cid,reviewer)
    approve(svc,cid,owner)
    before=repo.get_case(cid)
    with pytest.raises(ApprovalRequiredError):
        activate(svc,cid,owner)
    after=repo.get_case(cid)
    assert after.version==before.version
    assert len(after.events)==len(before.events)
    assert [e.event_type for e in after.events]==[e.event_type for e in before.events]
    repo.close()


def test_sql_approval_persists_without_implicit_activation(tmp_path):
    url,repo,svc,cid,owner,reviewer=setup_case(tmp_path)
    appr=condition(svc,cid,reviewer)
    assert appr.id==repo.approvals_for_case(cid)[-1].id
    assert repo.get_case(cid).status==CaseStatus.IN_REVIEW
    repo.close()
    reopened=SQLAlchemyKernelRepository(url)
    assert reopened.approvals_for_case(cid)[-1].conditions==appr.conditions
    assert reopened.get_case(cid).status==CaseStatus.IN_REVIEW
    reopened.close()


def test_sql_stale_snapshot_cannot_overwrite_newer_case_state(tmp_path):
    _,repo,svc,cid,owner,reviewer=setup_case(tmp_path)
    # Two readers get the same state/version. One commits a new event.
    stale=repo.get_case(cid)
    latest=repo.get_case(cid)
    latest.record_event(CaseEvent(event_type='FIRST_EDITOR_TEST_ONLY', actor_id=owner,details={}))
    repo.save_case(latest)
    # The older writer updates a stale status and new event at the same logical version.
    stale.status=CaseStatus.CLOSED
    stale.record_event(CaseEvent(event_type='SECOND_EDITOR_TEST_ONLY',actor_id=owner,details={}))
    with pytest.raises(StaleCaseWriteError):
        repo.save_case(stale)
    # The first writer's status and event survive the rejected stale write.
    assert repo.get_case(cid).status != CaseStatus.CLOSED
    repo.close()


@pytest.mark.xfail(strict=True,reason='No durable deny event is written on rejected attempted transition')
def test_sql_denied_activation_has_durable_denial_receipt(tmp_path):
    _,repo,svc,cid,owner,reviewer=setup_case(tmp_path)
    condition(svc,cid,reviewer)
    approve(svc,cid,owner)
    before=len(repo.get_case(cid).events)
    with pytest.raises(ApprovalRequiredError):
        activate(svc,cid,owner)
    assert len(repo.get_case(cid).events)>before
    repo.close()


@pytest.mark.xfail(strict=True,reason='No verified issuer epoch or grant expiry from Machine SSOT at this boundary')
def test_sql_authenticated_grant_expiry_evaluated(tmp_path):
    _,repo,svc,cid,owner,reviewer=setup_case(tmp_path)
    svc.record_approval(case_id=cid,approver_id=reviewer,decision=ApprovalDecision.APPROVE,
                        rationale='Fixture approved')
    approve(svc,cid,owner)
    repo.append_evidence(EvidenceReference(case_id=cid,label='EXPIRED_TEST_ONLY',
                                           uri='fixture://expiry-assertion',sensitivity=Sensitivity.ORANGE))
    with pytest.raises(ApprovalRequiredError):
        activate(svc,cid,owner)
    repo.close()


@pytest.mark.xfail(strict=True,reason='Late evidence review event has no trusted authority/standing contract')
def test_sql_authenticated_late_evidence_prevents_unconditional_activation(tmp_path):
    _,repo,svc,cid,owner,reviewer=setup_case(tmp_path)
    svc.record_approval(case_id=cid,approver_id=reviewer,decision=ApprovalDecision.APPROVE,
                        rationale='Fixture approved')
    approve(svc,cid,owner)
    case=repo.get_case(cid)
    case.record_event(CaseEvent(event_type='NEW_ADVERSE_EVIDENCE_TEST_ONLY', actor_id=owner,
                                details={'standing':'CONTESTED'}))
    repo.save_case(case)
    with pytest.raises(ApprovalRequiredError):
        activate(svc,cid,owner)
    repo.close()

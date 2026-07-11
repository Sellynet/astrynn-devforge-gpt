from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from astrynn_devforge.kernel import (
    CaseStatus,
    InMemoryKernelRepository,
    KernelService,
    Sensitivity,
)
from astrynn_devforge.vigilance import (
    ApprovalDecision,
    AuthorizationOutcome,
    GrantStatus,
    InMemoryVigilanceRepository,
    PermissionAction,
    PermissionApprovalError,
    PermissionBoundaryError,
    StalePermissionError,
    VigilancePermissionService,
)


def build_system(*, sensitivity: Sensitivity = Sensitivity.GREEN):
    kernel_repository = InMemoryKernelRepository()
    kernel = KernelService(kernel_repository)
    owner_id = uuid4()
    organization_id = uuid4()
    case = kernel.create_case(
        title="Vigilance governed permission case",
        description="Synthetic permission-boundary demonstration",
        owner_id=owner_id,
        organization_id=organization_id,
        sensitivity=sensitivity,
        actor_id=owner_id,
    )
    vigilance_repository = InMemoryVigilanceRepository()
    service = VigilancePermissionService(kernel_repository, vigilance_repository)
    return service, kernel_repository, vigilance_repository, case, owner_id


def create_draft(
    service,
    case,
    owner_id,
    *,
    subject_id=None,
    created_by=None,
    sensitivity=None,
    allowed_actions=(PermissionAction.READ, PermissionAction.SEND),
    denied_actions=(PermissionAction.DELETE, PermissionAction.EXECUTE),
    approval_required_actions=(PermissionAction.SEND,),
):
    now = datetime.now(UTC)
    return service.create_draft(
        case_id=case.id,
        blueprint_id=uuid4(),
        blueprint_version_id=uuid4(),
        blueprint_fingerprint="b" * 64,
        subject_id=subject_id or uuid4(),
        owner_id=owner_id,
        created_by=created_by or owner_id,
        tool_name="gmail_controlled",
        resource_prefixes=("gmail://threads/approved/",),
        allowed_actions=allowed_actions,
        denied_actions=denied_actions,
        approval_required_actions=approval_required_actions,
        sensitivity=sensitivity or case.sensitivity,
        reason="Minimum permissions for a synthetic customer-response assistant",
        review_at=now + timedelta(days=30),
        expires_at=now + timedelta(days=90),
    )


def activate(service, draft, approver_id):
    return service.activate_grant(
        grant_id=draft.grant_id,
        approver_id=approver_id,
        rationale="Scope, expiry, resources, and approval gates are explicit",
    )


def test_grant_starts_as_draft_and_uses_explicit_actions() -> None:
    service, kernel_repo, vigilance_repo, case, owner_id = build_system()
    draft = create_draft(service, case, owner_id)

    assert draft.status == GrantStatus.DRAFT
    assert draft.allowed_actions == (PermissionAction.READ, PermissionAction.SEND)
    assert PermissionAction.DELETE in draft.denied_actions
    assert len(draft.permission_fingerprint) == 64
    assert len(vigilance_repo.versions_for_grant(draft.grant_id)) == 1
    assert kernel_repo.get_case(case.id).status == CaseStatus.DRAFT


def test_sensitive_action_requires_named_human_approval() -> None:
    service, _, vigilance_repo, case, owner_id = build_system()
    subject_id = uuid4()
    evaluator_id = uuid4()
    draft = create_draft(service, case, owner_id, subject_id=subject_id)
    active, _ = activate(service, draft, owner_id)

    pending = service.authorize_action(
        grant_id=active.grant_id,
        subject_id=subject_id,
        action=PermissionAction.SEND,
        resource="gmail://threads/approved/42",
        evaluated_by=evaluator_id,
    )
    assert pending.outcome == AuthorizationOutcome.PENDING_APPROVAL

    request = service.request_action_approval(
        grant_id=active.grant_id,
        requested_by=subject_id,
        action=PermissionAction.SEND,
        resource="gmail://threads/approved/42",
        justification="Send the reviewed response to the named customer",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    decision = service.decide_action_request(
        request_id=request.id,
        approver_id=owner_id,
        decision=ApprovalDecision.APPROVE,
        rationale="The exact draft and recipient were reviewed",
    )
    allowed = service.authorize_action(
        grant_id=active.grant_id,
        subject_id=subject_id,
        action=PermissionAction.SEND,
        resource="gmail://threads/approved/42",
        evaluated_by=evaluator_id,
    )

    assert allowed.outcome == AuthorizationOutcome.ALLOWED
    assert allowed.approval_request_id == request.id
    assert allowed.approval_record_id == decision.id
    assert len(vigilance_repo.authorization_receipts_for_grant(active.grant_id)) == 2


def test_read_is_allowed_but_delete_and_out_of_scope_resources_are_denied() -> None:
    service, _, _, case, owner_id = build_system()
    subject_id = uuid4()
    draft = create_draft(service, case, owner_id, subject_id=subject_id)
    active, _ = activate(service, draft, owner_id)

    read = service.authorize_action(
        grant_id=active.grant_id,
        subject_id=subject_id,
        action=PermissionAction.READ,
        resource="gmail://threads/approved/7",
        evaluated_by=owner_id,
    )
    delete = service.authorize_action(
        grant_id=active.grant_id,
        subject_id=subject_id,
        action=PermissionAction.DELETE,
        resource="gmail://threads/approved/7",
        evaluated_by=owner_id,
    )
    outside = service.authorize_action(
        grant_id=active.grant_id,
        subject_id=subject_id,
        action=PermissionAction.READ,
        resource="gmail://admin/settings",
        evaluated_by=owner_id,
    )

    assert read.outcome == AuthorizationOutcome.ALLOWED
    assert delete.outcome == AuthorizationOutcome.DENIED
    assert outside.outcome == AuthorizationOutcome.DENIED


def test_agent_cannot_issue_or_approve_its_own_permissions() -> None:
    service, _, _, case, owner_id = build_system()
    subject_id = uuid4()

    with pytest.raises(PermissionBoundaryError, match="cannot issue"):
        create_draft(
            service,
            case,
            owner_id,
            subject_id=subject_id,
            created_by=subject_id,
        )

    draft = create_draft(service, case, owner_id, subject_id=subject_id)
    with pytest.raises(PermissionBoundaryError, match="cannot issue"):
        activate(service, draft, subject_id)


def test_emergency_disable_blocks_all_actions_and_preserves_history() -> None:
    service, _, vigilance_repo, case, owner_id = build_system()
    subject_id = uuid4()
    draft = create_draft(service, case, owner_id, subject_id=subject_id)
    active, _ = activate(service, draft, owner_id)
    disabled = service.emergency_disable(
        grant_id=active.grant_id,
        disabled_by=owner_id,
        reason="Unexpected tool-call pattern detected",
    )
    receipt = service.authorize_action(
        grant_id=active.grant_id,
        subject_id=subject_id,
        action=PermissionAction.READ,
        resource="gmail://threads/approved/7",
        evaluated_by=owner_id,
    )

    assert disabled.status == GrantStatus.SUSPENDED
    assert disabled.emergency_disabled is True
    assert receipt.outcome == AuthorizationOutcome.EMERGENCY_BLOCK
    assert len(vigilance_repo.versions_for_grant(active.grant_id)) == 3
    assert len(vigilance_repo.events_for_grant(active.grant_id)) >= 3


def test_revision_invalidates_old_action_approval() -> None:
    service, _, _, case, owner_id = build_system()
    subject_id = uuid4()
    draft = create_draft(service, case, owner_id, subject_id=subject_id)
    active, _ = activate(service, draft, owner_id)
    request = service.request_action_approval(
        grant_id=active.grant_id,
        requested_by=subject_id,
        action=PermissionAction.SEND,
        resource="gmail://threads/approved/88",
        justification="Reviewed customer response",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    service.decide_action_request(
        request_id=request.id,
        approver_id=owner_id,
        decision=ApprovalDecision.APPROVE,
        rationale="Approved exact send action",
    )
    now = datetime.now(UTC)
    revised = service.revise_grant(
        grant_id=active.grant_id,
        created_by=owner_id,
        tool_name="gmail_controlled",
        resource_prefixes=("gmail://threads/approved/",),
        allowed_actions=(PermissionAction.READ, PermissionAction.WRITE),
        denied_actions=(PermissionAction.SEND, PermissionAction.DELETE, PermissionAction.EXECUTE),
        approval_required_actions=(),
        reason="Remove external sending permission",
        review_at=now + timedelta(days=30),
        expires_at=now + timedelta(days=90),
        blueprint_version_id=uuid4(),
        blueprint_fingerprint="c" * 64,
    )

    assert revised.status == GrantStatus.DRAFT
    with pytest.raises(StalePermissionError):
        service.decide_action_request(
            request_id=request.id,
            approver_id=uuid4(),
            decision=ApprovalDecision.APPROVE,
            rationale="Attempt to reuse an obsolete request",
        )


def test_orange_grant_requires_owner_approver_separation() -> None:
    service, _, _, case, owner_id = build_system(sensitivity=Sensitivity.ORANGE)
    draft = create_draft(
        service,
        case,
        owner_id,
        sensitivity=Sensitivity.ORANGE,
    )

    with pytest.raises(PermissionApprovalError, match="separation"):
        activate(service, draft, owner_id)

    active, receipt = activate(service, draft, uuid4())
    assert active.status == GrantStatus.ACTIVE
    assert len(receipt.receipt_hash) == 64


def test_execution_record_requires_allowed_authorization() -> None:
    service, _, vigilance_repo, case, owner_id = build_system()
    subject_id = uuid4()
    draft = create_draft(service, case, owner_id, subject_id=subject_id)
    active, _ = activate(service, draft, owner_id)
    allowed = service.authorize_action(
        grant_id=active.grant_id,
        subject_id=subject_id,
        action=PermissionAction.READ,
        resource="gmail://threads/approved/5",
        evaluated_by=owner_id,
    )
    event = service.record_action_execution(
        authorization=allowed,
        recorded_by=owner_id,
        execution_reference="synthetic://execution/5",
    )

    assert event.details["authorization_receipt_hash"] == allowed.receipt_hash
    assert vigilance_repo.events_for_grant(active.grant_id)[-1].id == event.id

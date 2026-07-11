from uuid import uuid4

import pytest

from astrynn_devforge.kernel import (
    ApprovalDecision,
    ApprovalRequiredError,
    CaseStatus,
    InMemoryKernelRepository,
    InvalidTransitionError,
    KernelService,
    Sensitivity,
)


def build_service() -> KernelService:
    return KernelService(InMemoryKernelRepository())


def create_case(service: KernelService, *, sensitivity: Sensitivity = Sensitivity.GREEN):
    owner_id = uuid4()
    organization_id = uuid4()
    case = service.create_case(
        title="Aegis Clearance pilot",
        description="Controlled AI deployment assessment",
        owner_id=owner_id,
        organization_id=organization_id,
        sensitivity=sensitivity,
        actor_id=owner_id,
    )
    return case, owner_id


def test_case_requires_approval_before_approved_state() -> None:
    service = build_service()
    case, owner_id = create_case(service)
    service.transition_case(
        case_id=case.id,
        target=CaseStatus.IN_REVIEW,
        actor_id=owner_id,
        reason="Ready for assessment",
    )

    with pytest.raises(ApprovalRequiredError):
        service.transition_case(
            case_id=case.id,
            target=CaseStatus.APPROVED,
            actor_id=owner_id,
            reason="Attempt without approval",
        )


def test_green_case_can_be_approved_and_activated() -> None:
    service = build_service()
    case, owner_id = create_case(service)
    service.transition_case(
        case_id=case.id,
        target=CaseStatus.IN_REVIEW,
        actor_id=owner_id,
        reason="Assessment complete",
    )
    service.record_approval(
        case_id=case.id,
        approver_id=owner_id,
        decision=ApprovalDecision.APPROVE,
        rationale="Low sensitivity and controls verified",
    )
    approved = service.transition_case(
        case_id=case.id,
        target=CaseStatus.APPROVED,
        actor_id=owner_id,
        reason="Approved by owner",
    )
    active = service.transition_case(
        case_id=case.id,
        target=CaseStatus.ACTIVE,
        actor_id=owner_id,
        reason="Controlled activation",
    )

    assert approved.status is CaseStatus.APPROVED
    assert active.status is CaseStatus.ACTIVE
    assert len(active.events) == 5


def test_orange_case_requires_separate_approver() -> None:
    service = build_service()
    case, owner_id = create_case(service, sensitivity=Sensitivity.ORANGE)

    with pytest.raises(ApprovalRequiredError):
        service.record_approval(
            case_id=case.id,
            approver_id=owner_id,
            decision=ApprovalDecision.APPROVE,
            rationale="Self approval must be blocked",
        )


def test_conditional_approval_requires_conditions() -> None:
    service = build_service()
    case, _ = create_case(service)

    with pytest.raises(ValueError, match="at least one condition"):
        service.record_approval(
            case_id=case.id,
            approver_id=uuid4(),
            decision=ApprovalDecision.APPROVE_WITH_CONDITIONS,
            rationale="Controls are required",
        )


def test_invalid_transition_is_rejected() -> None:
    service = build_service()
    case, owner_id = create_case(service)

    with pytest.raises(InvalidTransitionError):
        service.transition_case(
            case_id=case.id,
            target=CaseStatus.ACTIVE,
            actor_id=owner_id,
            reason="Skipping review is forbidden",
        )


def test_repository_returns_defensive_copy() -> None:
    repository = InMemoryKernelRepository()
    service = KernelService(repository)
    case, _ = create_case(service)

    copy = repository.get_case(case.id)
    copy.title = "Tampered outside repository"

    assert repository.get_case(case.id).title == "Aegis Clearance pilot"

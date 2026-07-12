from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from .enums import ApprovalDecision, CaseStatus, Sensitivity
from .models import ApprovalRecord, Case, CaseEvent
from .repository import KernelRepository


class InvalidTransitionError(ValueError):
    pass


class ApprovalRequiredError(PermissionError):
    pass


@dataclass(frozen=True, slots=True)
class TransitionRule:
    source: CaseStatus
    target: CaseStatus


_ALLOWED_TRANSITIONS = {
    TransitionRule(CaseStatus.DRAFT, CaseStatus.IN_REVIEW),
    TransitionRule(CaseStatus.IN_REVIEW, CaseStatus.APPROVED),
    TransitionRule(CaseStatus.IN_REVIEW, CaseStatus.REJECTED),
    TransitionRule(CaseStatus.APPROVED, CaseStatus.ACTIVE),
    TransitionRule(CaseStatus.ACTIVE, CaseStatus.SUSPENDED),
    TransitionRule(CaseStatus.SUSPENDED, CaseStatus.ACTIVE),
    TransitionRule(CaseStatus.DRAFT, CaseStatus.CLOSED),
    TransitionRule(CaseStatus.REJECTED, CaseStatus.CLOSED),
    TransitionRule(CaseStatus.SUSPENDED, CaseStatus.CLOSED),
    TransitionRule(CaseStatus.ACTIVE, CaseStatus.CLOSED),
}


class KernelService:
    def __init__(self, repository: KernelRepository) -> None:
        self.repository = repository

    def create_case(
        self,
        *,
        title: str,
        description: str,
        owner_id: UUID,
        organization_id: UUID,
        sensitivity: Sensitivity,
        actor_id: UUID,
    ) -> Case:
        if not title.strip():
            raise ValueError("Case title is required")

        case = Case(
            title=title.strip(),
            description=description.strip(),
            owner_id=owner_id,
            organization_id=organization_id,
            sensitivity=sensitivity,
        )
        case.record_event(
            CaseEvent(
                event_type="CASE_CREATED",
                actor_id=actor_id,
                details={"status": case.status.value, "sensitivity": sensitivity.value},
            )
        )
        return self.repository.save_case(case)

    def transition_case(
        self,
        *,
        case_id: UUID,
        target: CaseStatus,
        actor_id: UUID,
        reason: str,
    ) -> Case:
        case = self.repository.get_case(case_id)
        rule = TransitionRule(case.status, target)
        if rule not in _ALLOWED_TRANSITIONS:
            raise InvalidTransitionError(f"Invalid transition: {case.status} -> {target}")

        if target in {CaseStatus.APPROVED, CaseStatus.ACTIVE}:
            self._assert_approval_allows(case_id, target)

        previous = case.status
        case.status = target
        case.record_event(
            CaseEvent(
                event_type="STATUS_CHANGED",
                actor_id=actor_id,
                details={"from": previous.value, "to": target.value, "reason": reason},
            )
        )
        return self.repository.save_case(case)

    def record_approval(
        self,
        *,
        case_id: UUID,
        approver_id: UUID,
        decision: ApprovalDecision,
        rationale: str,
        conditions: tuple[str, ...] = (),
    ) -> ApprovalRecord:
        case = self.repository.get_case(case_id)
        if case.owner_id == approver_id and case.sensitivity in {
            Sensitivity.ORANGE,
            Sensitivity.RED,
        }:
            raise ApprovalRequiredError(
                "Medium and high-sensitivity cases require separation between owner and approver"
            )
        if not rationale.strip():
            raise ValueError("Approval rationale is required")
        if decision == ApprovalDecision.APPROVE_WITH_CONDITIONS and not conditions:
            raise ValueError("Conditional approval requires at least one condition")

        approval = ApprovalRecord(
            case_id=case_id,
            approver_id=approver_id,
            decision=decision,
            rationale=rationale.strip(),
            conditions=conditions,
        )
        self.repository.append_approval(approval)

        case.record_event(
            CaseEvent(
                event_type="APPROVAL_RECORDED",
                actor_id=approver_id,
                details={
                    "decision": decision.value,
                    "conditions": list(conditions),
                    "approval_id": str(approval.id),
                },
            )
        )
        self.repository.save_case(case)
        return approval

    def _assert_approval_allows(self, case_id: UUID, target: CaseStatus) -> None:
        approvals = self.repository.approvals_for_case(case_id)
        if not approvals:
            raise ApprovalRequiredError(
                f"Approval required before moving case to {target.value}"
            )

        latest = approvals[-1]
        allowed = {
            ApprovalDecision.APPROVE,
            ApprovalDecision.APPROVE_WITH_CONDITIONS,
        }
        if latest.decision not in allowed:
            raise ApprovalRequiredError(
                f"Latest approval decision {latest.decision.value} blocks {target.value}"
            )

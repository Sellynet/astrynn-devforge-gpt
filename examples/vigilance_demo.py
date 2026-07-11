from __future__ import annotations

from datetime import UTC, datetime, timedelta
import json
from uuid import uuid4

from astrynn_devforge.kernel import InMemoryKernelRepository, KernelService, Sensitivity
from astrynn_devforge.vigilance import (
    ApprovalDecision,
    InMemoryVigilanceRepository,
    PermissionAction,
    VigilancePermissionService,
)


def main() -> None:
    kernel_repository = InMemoryKernelRepository()
    kernel = KernelService(kernel_repository)
    owner_id = uuid4()
    subject_id = uuid4()
    evaluator_id = uuid4()
    organization_id = uuid4()
    case = kernel.create_case(
        title="Synthetic governed Gmail draft assistant",
        description="Vigilance demonstration without credentials or tool execution",
        owner_id=owner_id,
        organization_id=organization_id,
        sensitivity=Sensitivity.GREEN,
        actor_id=owner_id,
    )

    vigilance_repository = InMemoryVigilanceRepository()
    vigilance = VigilancePermissionService(kernel_repository, vigilance_repository)
    now = datetime.now(UTC)
    draft = vigilance.create_draft(
        case_id=case.id,
        blueprint_id=uuid4(),
        blueprint_version_id=uuid4(),
        blueprint_fingerprint="b" * 64,
        subject_id=subject_id,
        owner_id=owner_id,
        created_by=owner_id,
        tool_name="gmail_controlled",
        resource_prefixes=("gmail://threads/approved/",),
        allowed_actions=(PermissionAction.READ, PermissionAction.SEND),
        denied_actions=(PermissionAction.DELETE, PermissionAction.EXECUTE),
        approval_required_actions=(PermissionAction.SEND,),
        sensitivity=Sensitivity.GREEN,
        reason="Read approved threads and send only after exact human approval",
        review_at=now + timedelta(days=30),
        expires_at=now + timedelta(days=90),
    )
    active, grant_receipt = vigilance.activate_grant(
        grant_id=draft.grant_id,
        approver_id=owner_id,
        rationale="Scope, expiry, and approval gates are explicit",
    )

    before_approval = vigilance.authorize_action(
        grant_id=active.grant_id,
        subject_id=subject_id,
        action=PermissionAction.SEND,
        resource="gmail://threads/approved/42",
        evaluated_by=evaluator_id,
    )
    request = vigilance.request_action_approval(
        grant_id=active.grant_id,
        requested_by=subject_id,
        action=PermissionAction.SEND,
        resource="gmail://threads/approved/42",
        justification="Send the exact draft already reviewed by the account owner",
        expires_at=now + timedelta(hours=1),
    )
    decision = vigilance.decide_action_request(
        request_id=request.id,
        approver_id=owner_id,
        decision=ApprovalDecision.APPROVE,
        rationale="Recipient, content, and scope were reviewed",
    )
    after_approval = vigilance.authorize_action(
        grant_id=active.grant_id,
        subject_id=subject_id,
        action=PermissionAction.SEND,
        resource="gmail://threads/approved/42",
        evaluated_by=evaluator_id,
    )
    event = vigilance.record_action_execution(
        authorization=after_approval,
        recorded_by=owner_id,
        execution_reference="synthetic://execution/send-42",
    )

    result = {
        "grant": active.to_dict(),
        "grant_receipt": grant_receipt.to_dict(),
        "before_approval": before_approval.to_dict(),
        "approval_request": request.to_dict(),
        "approval_decision": decision.to_dict(),
        "after_approval": after_approval.to_dict(),
        "recorded_event": event.to_dict(),
        "credentials_created": False,
        "tool_executed_by_vigilance": False,
        "kernel_case_status": kernel_repository.get_case(case.id).status.value,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

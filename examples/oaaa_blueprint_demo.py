from __future__ import annotations

import json
from uuid import uuid4

from astrynn_devforge.aegis import ClearanceDecision, ClearanceResult
from astrynn_devforge.aria import (
    ARIATestOutcome,
    ARIATestRegisterService,
    InMemoryARIARepository,
)
from astrynn_devforge.dataforge import (
    InMemoryOutputVaultRepository,
    OutputVaultService,
)
from astrynn_devforge.kernel import InMemoryKernelRepository, KernelService, Sensitivity
from astrynn_devforge.oaaa import (
    ApprovalPoint,
    ARIATestFamily,
    ARIATestRequirement,
    AutonomyLevel,
    DataBoundary,
    HumanDecision,
    InMemoryAgentBlueprintRepository,
    OAAAAgentBlueprintService,
    ToolPermission,
)


def main() -> None:
    kernel_repository = InMemoryKernelRepository()
    kernel = KernelService(kernel_repository)
    owner_id = uuid4()
    organization_id = uuid4()
    case = kernel.create_case(
        title="OAAA synthetic customer assistant",
        description="Governed blueprint demonstration with no runtime deployment",
        owner_id=owner_id,
        organization_id=organization_id,
        sensitivity=Sensitivity.GREEN,
        actor_id=owner_id,
    )

    vault_repository = InMemoryOutputVaultRepository()
    output_vault = OutputVaultService(kernel_repository, vault_repository)
    blueprint_repository = InMemoryAgentBlueprintRepository()
    oaaa = OAAAAgentBlueprintService(
        kernel_repository,
        blueprint_repository,
        output_vault,
    )

    draft = oaaa.create_draft(
        case_id=case.id,
        organization_id=organization_id,
        owner_id=owner_id,
        created_by=owner_id,
        name="Customer Evidence Assistant",
        business_need="Reduce response preparation time without autonomous sending",
        role="Prepare reviewable customer response drafts",
        objective="Prepare evidence-linked drafts for a named human reviewer",
        tools=(
            ToolPermission(
                name="gmail_draft",
                allowed_operations=("read_approved_thread", "create_draft"),
                prohibited_operations=("send", "delete"),
            ),
        ),
        data_boundary=DataBoundary(
            allowed_categories=("approved customer messages",),
            prohibited_categories=("credentials", "health data", "payment data"),
            retention_rule="Retain working context for no more than 30 days",
            deletion_rule="Delete context on case closure or owner request",
        ),
        allowed_actions=("read approved thread", "create response draft"),
        prohibited_actions=("send email", "delete email", "change permissions"),
        autonomy_level=AutonomyLevel.APPROVAL_GATED,
        approval_points=(
            ApprovalPoint(
                trigger="Before any external communication",
                approver_role="Named account owner",
            ),
        ),
        logs_required=("input source IDs", "tool calls", "human decisions"),
        aria_test_plan=(
            ARIATestRequirement(
                family=ARIATestFamily.PROMPT_INJECTION,
                objective="Reject hidden instructions in customer content",
                pass_criteria="Role and permissions remain unchanged",
            ),
            ARIATestRequirement(
                family=ARIATestFamily.TOOL_PERMISSION_DRIFT,
                objective="Prevent unapproved send or delete operations",
                pass_criteria="Only approved draft operations are requested",
            ),
            ARIATestRequirement(
                family=ARIATestFamily.INCIDENT_TRIGGER,
                objective="Stop and escalate on prohibited data or actions",
                pass_criteria="The agent stops, logs and escalates",
            ),
        ),
        rollback_procedure="Restore the last approved prompt and tool allow-list",
        disable_procedure="Revoke tool token and set blueprint to SUSPENDED",
        sensitivity=Sensitivity.GREEN,
    )
    submitted = oaaa.submit_for_review(
        blueprint_id=draft.blueprint_id,
        submitted_by=owner_id,
    )
    clearance = ClearanceResult(
        use_case_id=uuid4(),
        case_id=case.id,
        decision=ClearanceDecision.APTO_CON_CONTROLES,
        total_score=12,
        dimension_scores=(("data", 1), ("permissions", 2), ("autonomy", 1)),
        reasons=("The blueprint is bounded and approval-gated",),
        conditions=("Named human approval before external communication",),
        guardrails=(),
        specialist_triggers=(),
    )
    cleared = oaaa.record_clearance(
        blueprint_id=submitted.blueprint_id,
        clearance=clearance,
        assessed_blueprint_fingerprint=submitted.safety_fingerprint,
        recorded_by=owner_id,
    )
    approved, approval = oaaa.record_human_approval(
        blueprint_id=cleared.blueprint_id,
        approver_id=owner_id,
        decision=HumanDecision.APPROVE_WITH_CONDITIONS,
        rationale="Approve for synthetic sandbox use with a human send gate",
        conditions=("Synthetic or manually approved data only",),
    )

    aria_repository = InMemoryARIARepository()
    aria = ARIATestRegisterService(
        kernel_repository,
        blueprint_repository,
        aria_repository,
    )
    campaign = aria.create_campaign(
        blueprint_id=approved.blueprint_id,
        created_by=owner_id,
    )
    for family in campaign.required_families:
        aria.record_test(
            campaign_id=campaign.id,
            family=family,
            objective=f"Validate {family.value}",
            adversarial_input=f"Synthetic adversarial input for {family.value}",
            expected_behavior="Refuse, preserve boundaries and log the event",
            actual_behavior="The agent refused, preserved boundaries and logged the event",
            outcome=ARIATestOutcome.PASS,
            executed_by=owner_id,
            evidence_references=(f"evidence://aria/{family.value.lower()}",),
        )
    aria_receipt = aria.finalize_campaign(
        campaign_id=campaign.id,
        finalized_by=owner_id,
    )
    active, activation_receipt = oaaa.activate(
        blueprint_id=approved.blueprint_id,
        activated_by=owner_id,
        activation_note="Governance activation only; no runtime was deployed",
        aria_receipt=aria_receipt,
    )

    result = {
        "blueprint": active.to_dict(),
        "human_approval": approval.to_dict(),
        "aria_receipt": aria_receipt.to_dict(),
        "activation_receipt": activation_receipt.to_dict(),
        "kernel_case_status": kernel_repository.get_case(case.id).status.value,
        "runtime_deployed": False,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

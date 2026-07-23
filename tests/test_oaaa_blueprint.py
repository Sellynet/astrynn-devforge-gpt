from types import SimpleNamespace
from uuid import uuid4

import pytest

from astrynn_devforge.aegis import ClearanceDecision, ClearanceResult
from astrynn_devforge.dataforge import (
    InMemoryOutputVaultRepository,
    OutputVaultService,
)
from astrynn_devforge.kernel import (
    CaseStatus,
    InMemoryKernelRepository,
    KernelService,
    Sensitivity,
)
from astrynn_devforge.oaaa import (
    ApprovalPoint,
    ARIATestFamily,
    ARIATestRequirement,
    AutonomyLevel,
    BlueprintApprovalError,
    BlueprintStatus,
    DataBoundary,
    HumanDecision,
    InMemoryAgentBlueprintRepository,
    OAAAAgentBlueprintService,
    StaleClearanceError,
    ToolPermission,
)


def build_system(*, sensitivity: Sensitivity = Sensitivity.GREEN):
    kernel_repository = InMemoryKernelRepository()
    kernel = KernelService(kernel_repository)
    owner_id = uuid4()
    organization_id = uuid4()
    case = kernel.create_case(
        title="OAAA governed agent case",
        description="Synthetic blueprint assessment",
        owner_id=owner_id,
        organization_id=organization_id,
        sensitivity=sensitivity,
        actor_id=owner_id,
    )
    vault_repository = InMemoryOutputVaultRepository()
    output_vault = OutputVaultService(kernel_repository, vault_repository)
    blueprint_repository = InMemoryAgentBlueprintRepository()
    service = OAAAAgentBlueprintService(
        kernel_repository,
        blueprint_repository,
        output_vault,
    )
    return (
        service,
        kernel_repository,
        blueprint_repository,
        vault_repository,
        case,
        owner_id,
        organization_id,
    )


def blueprint_inputs(*, objective: str = "Prepare evidence-linked customer drafts"):
    return {
        "name": "Customer Evidence Assistant",
        "business_need": "Reduce response preparation time without autonomous sending",
        "role": "Prepare reviewable customer response drafts",
        "objective": objective,
        "tools": (
            ToolPermission(
                name="gmail_draft",
                allowed_operations=("read_approved_thread", "create_draft"),
                prohibited_operations=("send", "delete"),
                requires_human_approval=True,
            ),
        ),
        "data_boundary": DataBoundary(
            allowed_categories=("approved customer messages",),
            prohibited_categories=("credentials", "health data", "payment data"),
            retention_rule="Retain working context for no more than 30 days",
            deletion_rule="Delete working context on case closure or owner request",
        ),
        "allowed_actions": ("read approved thread", "create response draft"),
        "prohibited_actions": (
            "send email",
            "delete email",
            "change permissions",
            "deploy itself",
        ),
        "autonomy_level": AutonomyLevel.APPROVAL_GATED,
        "approval_points": (
            ApprovalPoint(
                trigger="Before any external communication",
                approver_role="Named account owner",
            ),
        ),
        "logs_required": (
            "input source IDs",
            "tool calls",
            "draft versions",
            "human decisions",
        ),
        "aria_test_plan": (
            ARIATestRequirement(
                family=ARIATestFamily.PROMPT_INJECTION,
                objective="Reject hidden instructions in customer content",
                pass_criteria="No hidden instruction changes role or permissions",
            ),
            ARIATestRequirement(
                family=ARIATestFamily.TOOL_PERMISSION_DRIFT,
                objective="Prevent unapproved send or delete operations",
                pass_criteria="Only explicitly allowed draft operations are requested",
            ),
            ARIATestRequirement(
                family=ARIATestFamily.INCIDENT_TRIGGER,
                objective="Stop and escalate on prohibited data or action requests",
                pass_criteria="Agent stops, logs and routes the event to the owner",
            ),
        ),
        "rollback_procedure": "Restore the last approved prompt and tool allow-list",
        "disable_procedure": "Revoke tool token and set the blueprint to SUSPENDED",
    }


def create_draft(service, case, owner_id, organization_id, *, sensitivity=None, **overrides):
    values = blueprint_inputs()
    values.update(overrides)
    return service.create_draft(
        case_id=case.id,
        organization_id=organization_id,
        owner_id=owner_id,
        created_by=owner_id,
        sensitivity=sensitivity or case.sensitivity,
        **values,
    )


def clearance_for(blueprint, decision=ClearanceDecision.APTO):
    conditions = (
        ("Human approval before every external action",)
        if decision == ClearanceDecision.APTO_CON_CONTROLES
        else ()
    )
    return ClearanceResult(
        use_case_id=uuid4(),
        case_id=blueprint.case_id,
        decision=decision,
        total_score=8,
        dimension_scores=(("data", 1), ("permissions", 1)),
        reasons=("Synthetic controlled test",),
        conditions=conditions,
        guardrails=(),
        specialist_triggers=(),
    )


def submit_and_clear(service, draft, owner_id, decision=ClearanceDecision.APTO):
    submitted = service.submit_for_review(
        blueprint_id=draft.blueprint_id,
        submitted_by=owner_id,
    )
    clearance = clearance_for(submitted, decision)
    cleared = service.record_clearance(
        blueprint_id=submitted.blueprint_id,
        clearance=clearance,
        assessed_blueprint_fingerprint=submitted.safety_fingerprint,
        recorded_by=owner_id,
    )
    return submitted, clearance, cleared


def passing_aria_receipt(blueprint):
    return SimpleNamespace(
        id=uuid4(),
        blueprint_id=blueprint.blueprint_id,
        blueprint_version_id=blueprint.id,
        blueprint_fingerprint=blueprint.safety_fingerprint,
        verdict="PASS",
        unresolved_critical_findings=0,
        receipt_hash="a" * 64,
    )


def test_blueprint_starts_as_draft_and_is_versioned_in_vault() -> None:
    service, kernel_repo, blueprint_repo, vault_repo, case, owner_id, org_id = build_system()
    draft = create_draft(service, case, owner_id, org_id)

    assert draft.status == BlueprintStatus.DRAFT
    assert draft.version == 1
    assert draft.vault_artifact_id is not None
    assert len(blueprint_repo.versions_for_blueprint(draft.blueprint_id)) == 1
    assert len(vault_repo.versions_for_artifact(draft.vault_artifact_id)) == 1
    assert kernel_repo.get_case(case.id).status == CaseStatus.DRAFT


def test_blueprint_rejects_wildcards_and_self_elevation_actions() -> None:
    service, _, _, _, case, owner_id, org_id = build_system()

    with pytest.raises(ValueError, match="Wildcard actions"):
        create_draft(
            service,
            case,
            owner_id,
            org_id,
            allowed_actions=("*",),
        )

    with pytest.raises(ValueError, match="safety boundary"):
        create_draft(
            service,
            case,
            owner_id,
            org_id,
            allowed_actions=("grant admin to itself",),
        )


def test_activation_is_blocked_without_clearance_and_human_approval() -> None:
    service, _, _, _, case, owner_id, org_id = build_system()
    draft = create_draft(service, case, owner_id, org_id)

    with pytest.raises(BlueprintApprovalError):
        service.activate(
            blueprint_id=draft.blueprint_id,
            activated_by=owner_id,
            activation_note="Attempt without gates",
        )


def test_stale_clearance_fingerprint_is_rejected() -> None:
    service, _, _, _, case, owner_id, org_id = build_system()
    draft = create_draft(service, case, owner_id, org_id)
    submitted = service.submit_for_review(
        blueprint_id=draft.blueprint_id,
        submitted_by=owner_id,
    )

    with pytest.raises(StaleClearanceError):
        service.record_clearance(
            blueprint_id=submitted.blueprint_id,
            clearance=clearance_for(submitted),
            assessed_blueprint_fingerprint="stale-fingerprint",
            recorded_by=owner_id,
        )


def test_no_apto_clearance_blocks_the_blueprint() -> None:
    service, _, _, _, case, owner_id, org_id = build_system()
    draft = create_draft(service, case, owner_id, org_id)
    _, _, blocked = submit_and_clear(
        service,
        draft,
        owner_id,
        decision=ClearanceDecision.NO_APTO_TODAVIA,
    )

    assert blocked.status == BlueprintStatus.BLOCKED
    assert blocked.clearance_decision == ClearanceDecision.NO_APTO_TODAVIA


def test_approved_blueprint_requires_aria_receipt_before_activation() -> None:
    service, _, _, _, case, owner_id, org_id = build_system()
    draft = create_draft(service, case, owner_id, org_id)
    _, _, cleared = submit_and_clear(service, draft, owner_id)
    approved, _ = service.record_human_approval(
        blueprint_id=cleared.blueprint_id,
        approver_id=owner_id,
        decision=HumanDecision.APPROVE,
        rationale="Scope and permissions are explicit",
    )

    with pytest.raises(BlueprintApprovalError, match="ARIA Receipt"):
        service.activate(
            blueprint_id=approved.blueprint_id,
            activated_by=owner_id,
            activation_note="Attempt without ARIA evidence",
        )


def test_happy_path_records_vault_and_aria_links_without_runtime_deployment() -> None:
    (
        service,
        kernel_repo,
        blueprint_repo,
        vault_repo,
        case,
        owner_id,
        org_id,
    ) = build_system()
    draft = create_draft(service, case, owner_id, org_id)
    _, clearance, cleared = submit_and_clear(service, draft, owner_id)
    approved, approval = service.record_human_approval(
        blueprint_id=cleared.blueprint_id,
        approver_id=owner_id,
        decision=HumanDecision.APPROVE,
        rationale="Scope, permissions, tests and rollback are explicit",
    )
    aria_receipt = passing_aria_receipt(approved)
    active, receipt = service.activate(
        blueprint_id=approved.blueprint_id,
        activated_by=owner_id,
        activation_note="Enable governance state for controlled sandbox use only",
        aria_receipt=aria_receipt,
    )

    assert clearance.id == active.clearance_result_id
    assert active.status == BlueprintStatus.ACTIVE
    assert active.human_approval_id == approval.id
    assert len(receipt.receipt_hash) == 64
    assert len(vault_repo.receipts_for_artifact(active.vault_artifact_id)) == 1
    assert len(blueprint_repo.activation_receipts_for_blueprint(active.blueprint_id)) == 1
    artifact_types = {
        item.artifact_type for item in kernel_repo.outputs_for_case(case.id)
    }
    assert "OAAA_ARIA_ACTIVATION_LINK" in artifact_types
    assert kernel_repo.get_case(case.id).status == CaseStatus.DRAFT


def test_orange_blueprint_requires_owner_approver_separation() -> None:
    service, _, _, _, case, owner_id, org_id = build_system(
        sensitivity=Sensitivity.ORANGE
    )
    draft = create_draft(
        service,
        case,
        owner_id,
        org_id,
        sensitivity=Sensitivity.ORANGE,
    )
    _, _, cleared = submit_and_clear(service, draft, owner_id)

    with pytest.raises(BlueprintApprovalError, match="separation"):
        service.record_human_approval(
            blueprint_id=cleared.blueprint_id,
            approver_id=owner_id,
            decision=HumanDecision.APPROVE,
            rationale="Owner cannot approve an ORANGE blueprint",
        )


def test_material_revision_invalidates_clearance_and_approval() -> None:
    service, _, _, _, case, owner_id, org_id = build_system()
    draft = create_draft(service, case, owner_id, org_id)
    _, _, cleared = submit_and_clear(service, draft, owner_id)
    revised = service.revise(
        blueprint_id=cleared.blueprint_id,
        created_by=owner_id,
        change_summary="Add urgency classification",
        **blueprint_inputs(
            objective="Prepare drafts and classify customer urgency for human review"
        ),
    )

    assert revised.status == BlueprintStatus.DRAFT
    assert revised.material_change is True
    assert revised.clearance_result_id is None
    assert revised.clearance_decision is None
    assert revised.human_approval_id is None


def test_safety_fingerprint_does_not_change_during_governance_transition() -> None:
    service, _, _, _, case, owner_id, org_id = build_system()
    draft = create_draft(service, case, owner_id, org_id)
    submitted = service.submit_for_review(
        blueprint_id=draft.blueprint_id,
        submitted_by=owner_id,
    )

    assert submitted.safety_fingerprint == draft.safety_fingerprint

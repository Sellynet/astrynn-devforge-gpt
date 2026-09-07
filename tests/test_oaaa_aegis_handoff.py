from dataclasses import replace
from uuid import uuid4

import pytest

from astrynn_devforge.aegis import (
    ClearanceDecision,
    ClearanceProofReceipt,
    RiskScores,
)
from astrynn_devforge.dataforge import InMemoryOutputVaultRepository, OutputVaultService
from astrynn_devforge.kernel import InMemoryKernelRepository, KernelService, Sensitivity
from astrynn_devforge.oaaa import (
    AegisHandoffContext,
    ApprovalPoint,
    ARIATestFamily,
    ARIATestRequirement,
    AutonomyLevel,
    BlueprintStatus,
    DataBoundary,
    HANDOFF_SCHEMA_VERSION,
    HandoffAcknowledgementState,
    HandoffRejectedError,
    InMemoryAgentBlueprintRepository,
    OAAAAgentBlueprintService,
    OAAAtoAegisHandoffService,
    ToolPermission,
)


def build_scores() -> RiskScores:
    return RiskScores(
        data=1,
        permissions=2,
        autonomy=2,
        impact=2,
        traceability=1,
        human_oversight=1,
        external_dependency=1,
        adversarial_robustness=2,
        incident_readiness=1,
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
            prohibited_categories=("credentials", "health data"),
            retention_rule="Retain working context for no more than 30 days",
            deletion_rule="Delete working context on case closure or owner request",
        ),
        "allowed_actions": ("read approved thread", "create response draft"),
        "prohibited_actions": ("send email", "delete email", "change permissions"),
        "autonomy_level": AutonomyLevel.APPROVAL_GATED,
        "approval_points": (
            ApprovalPoint(
                trigger="Before any external communication",
                approver_role="Named account owner",
            ),
        ),
        "logs_required": ("input source IDs", "tool calls", "human decisions"),
        "aria_test_plan": (
            ARIATestRequirement(
                family=ARIATestFamily.PROMPT_INJECTION,
                objective="Reject hidden instructions",
                pass_criteria="No hidden instruction changes role or permissions",
            ),
            ARIATestRequirement(
                family=ARIATestFamily.TOOL_PERMISSION_DRIFT,
                objective="Prevent unapproved operations",
                pass_criteria="Only explicitly allowed operations are requested",
            ),
            ARIATestRequirement(
                family=ARIATestFamily.INCIDENT_TRIGGER,
                objective="Stop on prohibited requests",
                pass_criteria="Agent stops, logs and escalates",
            ),
        ),
        "rollback_procedure": "Restore the last approved prompt and tool allow-list",
        "disable_procedure": "Revoke tool token and set the blueprint to SUSPENDED",
    }


def build_reviewed_blueprint():
    kernel_repository = InMemoryKernelRepository()
    kernel = KernelService(kernel_repository)
    owner_id = uuid4()
    organization_id = uuid4()
    case = kernel.create_case(
        title="G-01 bounded handoff",
        description="Synthetic OAAA to Aegis handoff assessment",
        owner_id=owner_id,
        organization_id=organization_id,
        sensitivity=Sensitivity.GREEN,
        actor_id=owner_id,
    )
    output_vault = OutputVaultService(
        kernel_repository,
        InMemoryOutputVaultRepository(),
    )
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
        sensitivity=Sensitivity.GREEN,
        **blueprint_inputs(),
    )
    submitted = oaaa.submit_for_review(
        blueprint_id=draft.blueprint_id,
        submitted_by=owner_id,
    )
    return oaaa, blueprint_repository, submitted, owner_id, organization_id


def build_context(blueprint, **overrides) -> AegisHandoffContext:
    values = {
        "case_id": blueprint.case_id,
        "organization_id": blueprint.organization_id,
        "owner_id": blueprint.owner_id,
        "sector": "B2B SaaS",
        "scores": build_scores(),
        "evidence_refs": ("aegis-intake://risk-context/g01-test",),
    }
    values.update(overrides)
    return AegisHandoffContext(**values)


def build_result(blueprint_repository, blueprint, **context_overrides):
    service = OAAAtoAegisHandoffService(blueprint_repository)
    result = service.build(
        blueprint_id=blueprint.blueprint_id,
        expected_source_safety_fingerprint=blueprint.safety_fingerprint,
        context=build_context(blueprint, **context_overrides),
    )
    return service, result


def clearance_receipt_for(result) -> ClearanceProofReceipt:
    return ClearanceProofReceipt(
        clearance_result_id=uuid4(),
        use_case_id=result.use_case.id,
        case_id=result.use_case.case_id,
        input_fingerprint=result.use_case.fingerprint(),
        decision=ClearanceDecision.APTO,
        total_score=result.use_case.scores.total,
        conditions=(),
        methodology_version="AEGIS-CLEARANCE-0.1",
    )


def test_identity_is_preserved_exactly() -> None:
    _, repo, blueprint, _, _ = build_reviewed_blueprint()
    _, result = build_result(repo, blueprint)

    assert result.handoff.case_id == blueprint.case_id == result.use_case.case_id
    assert result.handoff.organization_id == blueprint.organization_id == result.use_case.organization_id
    assert result.handoff.owner_id == blueprint.owner_id == result.use_case.owner_id


def test_same_source_and_context_produce_equivalent_aegis_payload_and_fingerprint() -> None:
    _, repo, blueprint, _, _ = build_reviewed_blueprint()
    service = OAAAtoAegisHandoffService(repo)
    context = build_context(blueprint)

    first = service.build(
        blueprint_id=blueprint.blueprint_id,
        expected_source_safety_fingerprint=blueprint.safety_fingerprint,
        context=context,
    )
    second = service.build(
        blueprint_id=blueprint.blueprint_id,
        expected_source_safety_fingerprint=blueprint.safety_fingerprint,
        context=context,
    )

    assert first.use_case.canonical_payload() == second.use_case.canonical_payload()
    assert first.use_case.fingerprint() == second.use_case.fingerprint()


def test_missing_sector_fails_closed() -> None:
    _, repo, blueprint, _, _ = build_reviewed_blueprint()
    service = OAAAtoAegisHandoffService(repo)

    with pytest.raises(HandoffRejectedError) as exc:
        service.build(
            blueprint_id=blueprint.blueprint_id,
            expected_source_safety_fingerprint=blueprint.safety_fingerprint,
            context=build_context(blueprint, sector=""),
        )

    assert exc.value.state == HandoffAcknowledgementState.REJECTED_INCOMPLETE


def test_missing_risk_scores_fails_closed() -> None:
    _, repo, blueprint, _, _ = build_reviewed_blueprint()
    service = OAAAtoAegisHandoffService(repo)

    with pytest.raises(HandoffRejectedError) as exc:
        service.build(
            blueprint_id=blueprint.blueprint_id,
            expected_source_safety_fingerprint=blueprint.safety_fingerprint,
            context=build_context(blueprint, scores=None),
        )

    assert exc.value.state == HandoffAcknowledgementState.REJECTED_INCOMPLETE


def test_cross_organization_context_is_rejected() -> None:
    _, repo, blueprint, _, _ = build_reviewed_blueprint()
    service = OAAAtoAegisHandoffService(repo)

    with pytest.raises(HandoffRejectedError) as exc:
        service.build(
            blueprint_id=blueprint.blueprint_id,
            expected_source_safety_fingerprint=blueprint.safety_fingerprint,
            context=build_context(blueprint, organization_id=uuid4()),
        )

    assert exc.value.state == HandoffAcknowledgementState.REJECTED_IDENTITY_MISMATCH


def test_mapping_is_bounded_and_unsupported_fields_are_explicit() -> None:
    _, repo, blueprint, _, _ = build_reviewed_blueprint()
    _, result = build_result(repo, blueprint)

    assert result.use_case.title == blueprint.name
    assert result.use_case.purpose == blueprint.business_need
    assert result.use_case.data_categories == blueprint.data_boundary.allowed_categories
    assert result.use_case.requested_actions == blueprint.allowed_actions
    assert "role" in result.handoff.unmapped_fields
    assert "tools" in result.handoff.unmapped_fields
    assert "prohibited_actions" in result.handoff.unmapped_fields


def test_tool_names_are_not_auto_mapped_to_systems() -> None:
    _, repo, blueprint, _, _ = build_reviewed_blueprint()
    _, result = build_result(repo, blueprint)

    assert blueprint.tools[0].name == "gmail_draft"
    assert result.use_case.systems == ()


def test_aria_requirements_are_not_auto_mapped_to_specialist_triggers() -> None:
    _, repo, blueprint, _, _ = build_reviewed_blueprint()
    _, result = build_result(repo, blueprint)

    assert blueprint.aria_test_plan
    assert result.use_case.specialist_triggers == ()


def test_approval_and_permission_semantics_do_not_become_authority() -> None:
    _, repo, blueprint, _, _ = build_reviewed_blueprint()
    _, result = build_result(repo, blueprint)

    assert blueprint.approval_points
    assert "approval_points" in result.handoff.unmapped_fields
    assert "authority" not in result.use_case.canonical_payload()


def test_acknowledgement_is_not_clearance() -> None:
    _, repo, blueprint, _, _ = build_reviewed_blueprint()
    _, result = build_result(repo, blueprint)

    assert result.acknowledgement.state == HandoffAcknowledgementState.ACCEPTED_FOR_EVALUATION
    assert result.handoff.target_use_case_id == result.use_case.id
    assert "decision" not in result.handoff.to_dict()


def test_clearance_receipt_binding_does_not_activate_or_execute_blueprint() -> None:
    _, repo, blueprint, _, _ = build_reviewed_blueprint()
    service, result = build_result(repo, blueprint)
    receipt = clearance_receipt_for(result)

    service.bind_clearance_receipt(result=result, receipt=receipt)

    assert repo.latest_version(blueprint.blueprint_id).status == BlueprintStatus.IN_REVIEW


def test_evidence_chain_binds_source_mapping_target_and_clearance_receipt() -> None:
    _, repo, blueprint, _, _ = build_reviewed_blueprint()
    service, result = build_result(repo, blueprint)
    receipt = clearance_receipt_for(result)

    evidence = service.bind_clearance_receipt(result=result, receipt=receipt)

    assert evidence.source_safety_fingerprint == blueprint.safety_fingerprint
    assert evidence.handoff_fingerprint == result.handoff.fingerprint
    assert evidence.target_use_case_id == result.use_case.id
    assert evidence.target_fingerprint == result.use_case.fingerprint()
    assert evidence.clearance_receipt_id == receipt.id
    assert evidence.clearance_input_fingerprint == result.use_case.fingerprint()


def test_changed_blueprint_invalidates_prior_handoff_clearance_applicability() -> None:
    _, repo, blueprint, _, _ = build_reviewed_blueprint()
    service, result = build_result(repo, blueprint)
    receipt = clearance_receipt_for(result)

    changed = replace(
        blueprint,
        id=uuid4(),
        parent_version_id=blueprint.id,
        version=blueprint.version + 1,
        status=BlueprintStatus.DRAFT,
        objective="Prepare drafts under a materially changed objective",
        material_change=True,
    )
    repo.append_version(changed)

    with pytest.raises(HandoffRejectedError) as exc:
        service.bind_clearance_receipt(result=result, receipt=receipt)

    assert exc.value.state == HandoffAcknowledgementState.REJECTED_STALE_SOURCE


def test_clearance_receipt_for_another_use_case_is_rejected() -> None:
    _, repo, blueprint, _, _ = build_reviewed_blueprint()
    service, result = build_result(repo, blueprint)
    receipt = replace(clearance_receipt_for(result), use_case_id=uuid4())

    with pytest.raises(HandoffRejectedError) as exc:
        service.bind_clearance_receipt(result=result, receipt=receipt)

    assert exc.value.state == HandoffAcknowledgementState.REJECTED_UNSUPPORTED_MAPPING


def test_unsupported_schema_version_is_rejected() -> None:
    _, repo, blueprint, _, _ = build_reviewed_blueprint()
    service = OAAAtoAegisHandoffService(repo)

    with pytest.raises(HandoffRejectedError) as exc:
        service.build(
            blueprint_id=blueprint.blueprint_id,
            expected_source_safety_fingerprint=blueprint.safety_fingerprint,
            context=build_context(blueprint),
            schema_version=f"{HANDOFF_SCHEMA_VERSION}-UNSUPPORTED",
        )

    assert exc.value.state == HandoffAcknowledgementState.REJECTED_SCHEMA_VERSION


def test_missing_supplemental_evidence_reference_is_rejected() -> None:
    _, repo, blueprint, _, _ = build_reviewed_blueprint()
    service = OAAAtoAegisHandoffService(repo)

    with pytest.raises(HandoffRejectedError) as exc:
        service.build(
            blueprint_id=blueprint.blueprint_id,
            expected_source_safety_fingerprint=blueprint.safety_fingerprint,
            context=build_context(blueprint, evidence_refs=()),
        )

    assert exc.value.state == HandoffAcknowledgementState.REJECTED_INCOMPLETE


def test_non_review_blueprint_is_not_eligible_for_handoff() -> None:
    oaaa, repo, blueprint, owner_id, _ = build_reviewed_blueprint()
    service = OAAAtoAegisHandoffService(repo)
    changed = replace(
        blueprint,
        id=uuid4(),
        parent_version_id=blueprint.id,
        version=blueprint.version + 1,
        status=BlueprintStatus.DRAFT,
        created_by=owner_id,
    )
    repo.append_version(changed)

    with pytest.raises(HandoffRejectedError) as exc:
        service.build(
            blueprint_id=blueprint.blueprint_id,
            expected_source_safety_fingerprint=changed.safety_fingerprint,
            context=build_context(changed),
        )

    assert exc.value.state == HandoffAcknowledgementState.REJECTED_UNSUPPORTED_MAPPING

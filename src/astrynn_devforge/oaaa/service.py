from __future__ import annotations

from dataclasses import replace
from uuid import UUID, uuid4

from astrynn_devforge.aegis import ClearanceDecision, ClearanceResult
from astrynn_devforge.dataforge import OutputVaultService, VaultDecision
from astrynn_devforge.kernel import (
    ArtifactStatus,
    EvidenceReference,
    InMemoryKernelRepository,
    OutputArtifact,
    Sensitivity,
)

from .enums import AutonomyLevel, BlueprintStatus, HumanDecision
from .models import (
    ARIATestRequirement,
    ActivationReceipt,
    AgentBlueprintVersion,
    ApprovalPoint,
    DataBoundary,
    HumanApprovalRecord,
    ToolPermission,
    utc_now,
)
from .repository import InMemoryAgentBlueprintRepository


class BlueprintTransitionError(ValueError):
    pass


class BlueprintApprovalError(PermissionError):
    pass


class StaleClearanceError(ValueError):
    pass


class OAAAAgentBlueprintService:
    """Governed agent-design workflow. ACTIVE is a governance state, not deployment."""

    def __init__(
        self,
        kernel_repository: InMemoryKernelRepository,
        blueprint_repository: InMemoryAgentBlueprintRepository,
        output_vault: OutputVaultService,
    ) -> None:
        self.kernel_repository = kernel_repository
        self.blueprint_repository = blueprint_repository
        self.output_vault = output_vault

    def create_draft(
        self,
        *,
        case_id: UUID,
        organization_id: UUID,
        owner_id: UUID,
        created_by: UUID,
        name: str,
        business_need: str,
        role: str,
        objective: str,
        tools: tuple[ToolPermission, ...],
        data_boundary: DataBoundary,
        allowed_actions: tuple[str, ...],
        prohibited_actions: tuple[str, ...],
        autonomy_level: AutonomyLevel,
        approval_points: tuple[ApprovalPoint, ...],
        logs_required: tuple[str, ...],
        aria_test_plan: tuple[ARIATestRequirement, ...],
        rollback_procedure: str,
        disable_procedure: str,
        sensitivity: Sensitivity,
    ) -> AgentBlueprintVersion:
        case = self.kernel_repository.get_case(case_id)
        self._assert_sensitivity_allowed(case.sensitivity, sensitivity)
        if case.organization_id != organization_id:
            raise ValueError("Blueprint organization must match the Kernel case")
        if case.owner_id != owner_id:
            raise ValueError("Blueprint owner must match the Kernel case owner")

        blueprint_id = uuid4()
        preliminary = AgentBlueprintVersion(
            blueprint_id=blueprint_id,
            case_id=case_id,
            organization_id=organization_id,
            owner_id=owner_id,
            created_by=created_by,
            name=name,
            business_need=business_need,
            role=role,
            objective=objective,
            tools=tools,
            data_boundary=data_boundary,
            allowed_actions=allowed_actions,
            prohibited_actions=prohibited_actions,
            autonomy_level=autonomy_level,
            approval_points=approval_points,
            logs_required=logs_required,
            aria_test_plan=aria_test_plan,
            rollback_procedure=rollback_procedure,
            disable_procedure=disable_procedure,
            sensitivity=sensitivity,
            version=1,
            status=BlueprintStatus.DRAFT,
            material_change=True,
            change_summary="Initial governed blueprint draft",
            status_reason="Awaiting review, Aegis Clearance and named human approval",
        )
        test_references = tuple(
            f"aria-plan:{requirement.family.value}" for requirement in aria_test_plan
        )
        evidence_references = (f"oaaa://blueprints/{blueprint_id}/versions/1",)
        vault_artifact = self.output_vault.create_draft(
            case_id=case_id,
            owner_id=owner_id,
            created_by=created_by,
            artifact_type="OAAA_AGENT_BLUEPRINT",
            title=name,
            content=preliminary.to_dict(),
            sensitivity=sensitivity,
            test_references=test_references,
            evidence_references=evidence_references,
            change_summary="Initial OAAA blueprint",
        )
        blueprint = replace(preliminary, vault_artifact_id=vault_artifact.artifact_id)
        return self._append_blueprint(blueprint)

    def revise(
        self,
        *,
        blueprint_id: UUID,
        created_by: UUID,
        name: str,
        business_need: str,
        role: str,
        objective: str,
        tools: tuple[ToolPermission, ...],
        data_boundary: DataBoundary,
        allowed_actions: tuple[str, ...],
        prohibited_actions: tuple[str, ...],
        autonomy_level: AutonomyLevel,
        approval_points: tuple[ApprovalPoint, ...],
        logs_required: tuple[str, ...],
        aria_test_plan: tuple[ARIATestRequirement, ...],
        rollback_procedure: str,
        disable_procedure: str,
        change_summary: str,
    ) -> AgentBlueprintVersion:
        latest = self.blueprint_repository.latest_version(blueprint_id)
        if latest.status == BlueprintStatus.ACTIVE:
            raise BlueprintTransitionError("Suspend an ACTIVE blueprint before revising it")
        if latest.status == BlueprintStatus.SUPERSEDED:
            raise BlueprintTransitionError("A SUPERSEDED blueprint cannot be revised")
        if not change_summary.strip():
            raise ValueError("Revision change summary is required")

        candidate = AgentBlueprintVersion(
            blueprint_id=latest.blueprint_id,
            case_id=latest.case_id,
            organization_id=latest.organization_id,
            owner_id=latest.owner_id,
            created_by=created_by,
            name=name,
            business_need=business_need,
            role=role,
            objective=objective,
            tools=tools,
            data_boundary=data_boundary,
            allowed_actions=allowed_actions,
            prohibited_actions=prohibited_actions,
            autonomy_level=autonomy_level,
            approval_points=approval_points,
            logs_required=logs_required,
            aria_test_plan=aria_test_plan,
            rollback_procedure=rollback_procedure,
            disable_procedure=disable_procedure,
            sensitivity=latest.sensitivity,
            version=latest.version + 1,
            status=BlueprintStatus.DRAFT,
            material_change=False,
            vault_artifact_id=latest.vault_artifact_id,
            parent_version_id=latest.id,
            change_summary=change_summary,
            status_reason="Revision requires review before any activation state",
        )
        material_change = candidate.safety_fingerprint != latest.safety_fingerprint
        candidate = replace(
            candidate,
            material_change=material_change,
            status_reason=(
                "Material change invalidated prior clearance and approval"
                if material_change
                else "Non-material revision requires controlled resubmission"
            ),
        )
        if candidate.vault_artifact_id is None:
            raise BlueprintTransitionError("Blueprint is not linked to Output Vault")
        self.output_vault.revise(
            artifact_id=candidate.vault_artifact_id,
            created_by=created_by,
            content=candidate.to_dict(),
            change_summary=change_summary,
            test_references=tuple(
                f"aria-plan:{requirement.family.value}" for requirement in aria_test_plan
            ),
            evidence_references=(
                f"oaaa://blueprints/{blueprint_id}/versions/{candidate.version}",
            ),
        )
        return self._append_blueprint(candidate)

    def submit_for_review(
        self,
        *,
        blueprint_id: UUID,
        submitted_by: UUID,
        reason: str = "Submitted for OAAA review",
    ) -> AgentBlueprintVersion:
        latest = self.blueprint_repository.latest_version(blueprint_id)
        if latest.status != BlueprintStatus.DRAFT:
            raise BlueprintTransitionError("Only a DRAFT blueprint can enter review")
        if latest.vault_artifact_id is None:
            raise BlueprintTransitionError("Blueprint is not linked to Output Vault")
        self.output_vault.submit_for_review(
            artifact_id=latest.vault_artifact_id,
            submitted_by=submitted_by,
            change_summary=reason,
        )
        reviewed = self._new_version(
            latest,
            created_by=submitted_by,
            status=BlueprintStatus.IN_REVIEW,
            material_change=latest.material_change,
            status_reason=reason,
        )
        return self._append_blueprint(reviewed)

    def record_clearance(
        self,
        *,
        blueprint_id: UUID,
        clearance: ClearanceResult,
        assessed_blueprint_fingerprint: str,
        recorded_by: UUID,
    ) -> AgentBlueprintVersion:
        latest = self.blueprint_repository.latest_version(blueprint_id)
        if latest.status != BlueprintStatus.IN_REVIEW:
            raise BlueprintTransitionError("Aegis Clearance requires a blueprint IN_REVIEW")
        if clearance.case_id != latest.case_id:
            raise ValueError("Aegis Clearance must belong to the same Kernel case")
        if assessed_blueprint_fingerprint != latest.safety_fingerprint:
            raise StaleClearanceError(
                "The clearance was not issued for the latest blueprint safety fingerprint"
            )

        deployable = {
            ClearanceDecision.APTO,
            ClearanceDecision.APTO_CON_CONTROLES,
        }
        status = (
            BlueprintStatus.CLEARED
            if clearance.decision in deployable
            else BlueprintStatus.BLOCKED
        )
        reason = (
            "Aegis Clearance passed; named human approval is still required"
            if status == BlueprintStatus.CLEARED
            else f"Aegis decision {clearance.decision.value} blocks activation"
        )
        cleared = self._new_version(
            latest,
            created_by=recorded_by,
            status=status,
            material_change=latest.material_change,
            clearance_result_id=clearance.id,
            clearance_decision=clearance.decision,
            clearance_conditions=clearance.conditions,
            clearance_guardrail_codes=tuple(item.code for item in clearance.guardrails),
            status_reason=reason,
        )
        stored = self._append_blueprint(cleared)
        self.kernel_repository.append_evidence(
            EvidenceReference(
                case_id=stored.case_id,
                label=f"OAAA Aegis Clearance for blueprint v{stored.version}",
                uri=f"aegis://clearances/{clearance.id}",
                sensitivity=stored.sensitivity,
            )
        )
        return stored

    def record_human_approval(
        self,
        *,
        blueprint_id: UUID,
        approver_id: UUID,
        decision: HumanDecision,
        rationale: str,
        conditions: tuple[str, ...] = (),
    ) -> tuple[AgentBlueprintVersion, HumanApprovalRecord]:
        latest = self.blueprint_repository.latest_version(blueprint_id)
        if latest.status != BlueprintStatus.CLEARED:
            raise BlueprintTransitionError("Human approval requires a CLEARED blueprint")
        if latest.clearance_result_id is None or latest.clearance_decision is None:
            raise BlueprintApprovalError("The blueprint has no valid Aegis Clearance")
        if not rationale.strip():
            raise ValueError("Human approval rationale is required")
        if decision == HumanDecision.APPROVE_WITH_CONDITIONS and not conditions:
            raise ValueError("Conditional approval requires explicit conditions")

        case = self.kernel_repository.get_case(latest.case_id)
        if case.sensitivity in {Sensitivity.ORANGE, Sensitivity.RED}:
            if approver_id == latest.owner_id:
                raise BlueprintApprovalError(
                    "ORANGE and RED blueprints require separation between owner and approver"
                )
        if latest.vault_artifact_id is None:
            raise BlueprintTransitionError("Blueprint is not linked to Output Vault")

        vault_decision = {
            HumanDecision.APPROVE: VaultDecision.APPROVED,
            HumanDecision.APPROVE_WITH_CONDITIONS: VaultDecision.APPROVED_WITH_CONDITIONS,
            HumanDecision.REJECT: VaultDecision.REJECTED,
        }[decision]
        combined_conditions = tuple(
            dict.fromkeys((*latest.clearance_conditions, *conditions))
        )
        vault_package = self.output_vault.record_decision(
            artifact_id=latest.vault_artifact_id,
            evaluator_id=approver_id,
            decision=vault_decision,
            conditions=combined_conditions,
            rationale=rationale,
        )
        approval = HumanApprovalRecord(
            blueprint_id=latest.blueprint_id,
            blueprint_version_id=latest.id,
            blueprint_fingerprint=latest.safety_fingerprint,
            approver_id=approver_id,
            decision=decision,
            rationale=rationale,
            conditions=combined_conditions,
            clearance_result_id=latest.clearance_result_id,
            vault_receipt_id=vault_package.receipt.id,
            vault_receipt_hash=vault_package.receipt.receipt_hash,
        )
        stored_approval = self.blueprint_repository.append_approval(approval)
        approved_status = (
            BlueprintStatus.BLOCKED
            if decision == HumanDecision.REJECT
            else BlueprintStatus.APPROVED
        )
        approved = self._new_version(
            latest,
            created_by=approver_id,
            status=approved_status,
            material_change=latest.material_change,
            human_approval_id=stored_approval.id,
            status_reason=(
                "Named human approval recorded; governance activation is permitted"
                if approved_status == BlueprintStatus.APPROVED
                else "Named human reviewer rejected the blueprint"
            ),
        )
        stored_blueprint = self._append_blueprint(approved)
        self.kernel_repository.append_evidence(
            EvidenceReference(
                case_id=stored_blueprint.case_id,
                label=f"OAAA named human decision for blueprint v{stored_blueprint.version}",
                uri=f"oaaa://approvals/{stored_approval.id}",
                sensitivity=stored_blueprint.sensitivity,
            )
        )
        return stored_blueprint, stored_approval

    def activate(
        self,
        *,
        blueprint_id: UUID,
        activated_by: UUID,
        activation_note: str,
    ) -> tuple[AgentBlueprintVersion, ActivationReceipt]:
        latest = self.blueprint_repository.latest_version(blueprint_id)
        if latest.status != BlueprintStatus.APPROVED:
            raise BlueprintApprovalError(
                "Activation requires Aegis Clearance and named human approval"
            )
        if latest.clearance_decision not in {
            ClearanceDecision.APTO,
            ClearanceDecision.APTO_CON_CONTROLES,
        }:
            raise BlueprintApprovalError("The recorded Aegis decision does not permit activation")
        if latest.clearance_result_id is None or latest.human_approval_id is None:
            raise BlueprintApprovalError("Activation gates are incomplete")
        if not activation_note.strip():
            raise ValueError("Activation note is required")

        approvals = self.blueprint_repository.approvals_for_blueprint(blueprint_id)
        approval = next(
            (record for record in reversed(approvals) if record.id == latest.human_approval_id),
            None,
        )
        if approval is None:
            raise BlueprintApprovalError("Named human approval evidence is missing")
        if approval.decision == HumanDecision.REJECT:
            raise BlueprintApprovalError("A rejected blueprint cannot be activated")
        if approval.blueprint_fingerprint != latest.safety_fingerprint:
            raise StaleClearanceError("Human approval belongs to a different blueprint fingerprint")

        active = self._new_version(
            latest,
            created_by=activated_by,
            status=BlueprintStatus.ACTIVE,
            material_change=latest.material_change,
            status_reason=(
                "Governance state ACTIVE; no runtime deployment or external action was executed"
            ),
        )
        stored = self._append_blueprint(active)
        receipt = ActivationReceipt(
            blueprint_id=stored.blueprint_id,
            blueprint_version_id=stored.id,
            blueprint_fingerprint=stored.safety_fingerprint,
            clearance_result_id=stored.clearance_result_id,
            clearance_decision=stored.clearance_decision,
            human_approval_id=stored.human_approval_id,
            activated_by=activated_by,
            activation_note=activation_note,
            vault_receipt_id=approval.vault_receipt_id,
            vault_receipt_hash=approval.vault_receipt_hash,
        )
        stored_receipt = self.blueprint_repository.append_activation_receipt(receipt)
        self.kernel_repository.append_output(
            OutputArtifact(
                case_id=stored.case_id,
                artifact_type="OAAA_ACTIVATION_RECEIPT",
                owner_id=stored.owner_id,
                content=stored_receipt.to_dict(),
                version=stored.version,
                status=ArtifactStatus.APPROVED,
            )
        )
        self.kernel_repository.append_evidence(
            EvidenceReference(
                case_id=stored.case_id,
                label=f"OAAA Activation Receipt v{stored.version}",
                uri=f"oaaa://activations/{stored_receipt.id}",
                sensitivity=stored.sensitivity,
            )
        )
        return stored, stored_receipt

    def suspend(
        self,
        *,
        blueprint_id: UUID,
        suspended_by: UUID,
        reason: str,
    ) -> AgentBlueprintVersion:
        latest = self.blueprint_repository.latest_version(blueprint_id)
        if latest.status != BlueprintStatus.ACTIVE:
            raise BlueprintTransitionError("Only an ACTIVE blueprint can be suspended")
        if not reason.strip():
            raise ValueError("Suspension reason is required")
        suspended = self._new_version(
            latest,
            created_by=suspended_by,
            status=BlueprintStatus.SUSPENDED,
            material_change=latest.material_change,
            status_reason=reason,
        )
        stored = self._append_blueprint(suspended)
        self.kernel_repository.append_evidence(
            EvidenceReference(
                case_id=stored.case_id,
                label=f"OAAA blueprint suspended at v{stored.version}",
                uri=f"oaaa://blueprints/{stored.blueprint_id}/suspensions/{stored.id}",
                sensitivity=stored.sensitivity,
            )
        )
        return stored

    def _new_version(
        self,
        latest: AgentBlueprintVersion,
        *,
        created_by: UUID,
        status: BlueprintStatus,
        material_change: bool,
        **changes: object,
    ) -> AgentBlueprintVersion:
        return replace(
            latest,
            id=uuid4(),
            created_at=utc_now(),
            version=latest.version + 1,
            parent_version_id=latest.id,
            created_by=created_by,
            status=status,
            material_change=material_change,
            **changes,
        )

    def _append_blueprint(
        self, blueprint: AgentBlueprintVersion
    ) -> AgentBlueprintVersion:
        stored = self.blueprint_repository.append_version(blueprint)
        self.kernel_repository.append_evidence(
            EvidenceReference(
                case_id=stored.case_id,
                label=f"OAAA blueprint {stored.status.value} v{stored.version}",
                uri=(
                    f"oaaa://blueprints/{stored.blueprint_id}/versions/{stored.version}"
                ),
                sensitivity=stored.sensitivity,
            )
        )
        return stored

    @staticmethod
    def _assert_sensitivity_allowed(
        case_sensitivity: Sensitivity,
        blueprint_sensitivity: Sensitivity,
    ) -> None:
        order = {
            Sensitivity.GREEN: 0,
            Sensitivity.ORANGE: 1,
            Sensitivity.RED: 2,
        }
        if order[blueprint_sensitivity] > order[case_sensitivity]:
            raise BlueprintApprovalError(
                "Blueprint sensitivity cannot exceed the Kernel case sensitivity"
            )

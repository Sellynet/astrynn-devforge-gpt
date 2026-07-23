from __future__ import annotations

from copy import deepcopy
from typing import Any
from uuid import UUID, uuid4

from astrynn_devforge.kernel import (
    ArtifactStatus,
    EvidenceReference,
    InMemoryKernelRepository,
    OutputArtifact,
    Sensitivity,
)

from .enums import VaultDecision
from .models import VaultArtifactVersion, VaultDecisionPackage, VaultProofReceipt
from .repository import InMemoryOutputVaultRepository


class InvalidArtifactTransitionError(ValueError):
    pass


class VaultApprovalError(PermissionError):
    pass


class OutputVaultService:
    def __init__(
        self,
        kernel_repository: InMemoryKernelRepository,
        vault_repository: InMemoryOutputVaultRepository,
    ) -> None:
        self.kernel_repository = kernel_repository
        self.vault_repository = vault_repository

    def create_draft(
        self,
        *,
        case_id: UUID,
        owner_id: UUID,
        created_by: UUID,
        artifact_type: str,
        title: str,
        content: dict[str, Any],
        sensitivity: Sensitivity,
        test_references: tuple[str, ...] = (),
        evidence_references: tuple[str, ...] = (),
        change_summary: str = "Initial draft",
    ) -> VaultArtifactVersion:
        case = self.kernel_repository.get_case(case_id)
        self._assert_sensitivity_allowed(case.sensitivity, sensitivity)
        artifact = VaultArtifactVersion(
            artifact_id=uuid4(),
            case_id=case_id,
            owner_id=owner_id,
            created_by=created_by,
            artifact_type=artifact_type,
            title=title,
            content=deepcopy(content),
            sensitivity=sensitivity,
            version=1,
            status=ArtifactStatus.DRAFT,
            test_references=test_references,
            evidence_references=evidence_references,
            change_summary=change_summary,
        )
        return self._append_and_mirror(artifact)

    def revise(
        self,
        *,
        artifact_id: UUID,
        created_by: UUID,
        content: dict[str, Any],
        change_summary: str,
        test_references: tuple[str, ...] | None = None,
        evidence_references: tuple[str, ...] | None = None,
    ) -> VaultArtifactVersion:
        latest = self.vault_repository.latest_version(artifact_id)
        if latest.status == ArtifactStatus.SUPERSEDED:
            raise InvalidArtifactTransitionError("A superseded artifact lineage cannot be revised")
        if not change_summary.strip():
            raise ValueError("Revision change summary is required")
        artifact = VaultArtifactVersion(
            artifact_id=latest.artifact_id,
            case_id=latest.case_id,
            owner_id=latest.owner_id,
            created_by=created_by,
            artifact_type=latest.artifact_type,
            title=latest.title,
            content=deepcopy(content),
            sensitivity=latest.sensitivity,
            version=latest.version + 1,
            status=ArtifactStatus.DRAFT,
            test_references=(
                latest.test_references if test_references is None else test_references
            ),
            evidence_references=(
                latest.evidence_references
                if evidence_references is None
                else evidence_references
            ),
            parent_version_id=latest.id,
            change_summary=change_summary,
        )
        return self._append_and_mirror(artifact)

    def submit_for_review(
        self,
        *,
        artifact_id: UUID,
        submitted_by: UUID,
        change_summary: str = "Submitted for review",
    ) -> VaultArtifactVersion:
        latest = self.vault_repository.latest_version(artifact_id)
        if latest.status != ArtifactStatus.DRAFT:
            raise InvalidArtifactTransitionError("Only a DRAFT artifact can enter REVIEW")
        artifact = self._copy_as_new_version(
            latest=latest,
            created_by=submitted_by,
            status=ArtifactStatus.REVIEW,
            decision=None,
            conditions=(),
            change_summary=change_summary,
        )
        return self._append_and_mirror(artifact)

    def record_decision(
        self,
        *,
        artifact_id: UUID,
        evaluator_id: UUID,
        decision: VaultDecision,
        conditions: tuple[str, ...] = (),
        rationale: str,
    ) -> VaultDecisionPackage:
        latest = self.vault_repository.latest_version(artifact_id)
        if latest.status != ArtifactStatus.REVIEW:
            raise InvalidArtifactTransitionError("Only an artifact in REVIEW can receive a decision")
        if not rationale.strip():
            raise ValueError("Decision rationale is required")

        case = self.kernel_repository.get_case(latest.case_id)
        if case.sensitivity in {Sensitivity.ORANGE, Sensitivity.RED} and evaluator_id == latest.owner_id:
            raise VaultApprovalError(
                "ORANGE and RED artifacts require separation between owner and evaluator"
            )
        if not latest.evidence_references:
            raise VaultApprovalError("A decision requires at least one evidence reference")
        if (
            decision in {VaultDecision.APPROVED, VaultDecision.APPROVED_WITH_CONDITIONS}
            and not latest.test_references
        ):
            raise VaultApprovalError("Approval requires at least one test reference")

        status = self._status_for_decision(decision)
        artifact = self._copy_as_new_version(
            latest=latest,
            created_by=evaluator_id,
            status=status,
            decision=decision,
            conditions=conditions,
            change_summary=rationale,
        )
        stored = self._append_and_mirror(artifact)
        receipt = VaultProofReceipt(
            artifact_id=stored.artifact_id,
            artifact_version_id=stored.id,
            case_id=stored.case_id,
            version=stored.version,
            evaluator_id=evaluator_id,
            decision=decision,
            conditions=conditions,
            test_references=stored.test_references,
            evidence_references=stored.evidence_references,
            artifact_integrity_hash=stored.integrity_hash,
        )
        stored_receipt = self.vault_repository.append_receipt(receipt)
        self.kernel_repository.append_evidence(
            EvidenceReference(
                case_id=stored.case_id,
                label=f"Output Vault Proof Receipt v{stored.version}",
                uri=f"vault://receipts/{stored_receipt.id}",
                sensitivity=stored.sensitivity,
            )
        )
        return VaultDecisionPackage(artifact=stored, receipt=stored_receipt)

    def supersede(
        self,
        *,
        artifact_id: UUID,
        actor_id: UUID,
        reason: str,
    ) -> VaultArtifactVersion:
        latest = self.vault_repository.latest_version(artifact_id)
        if latest.status != ArtifactStatus.APPROVED:
            raise InvalidArtifactTransitionError("Only an APPROVED artifact can be superseded")
        if not reason.strip():
            raise ValueError("Supersession reason is required")
        artifact = self._copy_as_new_version(
            latest=latest,
            created_by=actor_id,
            status=ArtifactStatus.SUPERSEDED,
            decision=latest.decision,
            conditions=latest.conditions,
            change_summary=reason,
        )
        return self._append_and_mirror(artifact)

    def _copy_as_new_version(
        self,
        *,
        latest: VaultArtifactVersion,
        created_by: UUID,
        status: ArtifactStatus,
        decision: VaultDecision | None,
        conditions: tuple[str, ...],
        change_summary: str,
    ) -> VaultArtifactVersion:
        return VaultArtifactVersion(
            artifact_id=latest.artifact_id,
            case_id=latest.case_id,
            owner_id=latest.owner_id,
            created_by=created_by,
            artifact_type=latest.artifact_type,
            title=latest.title,
            content=deepcopy(latest.content),
            sensitivity=latest.sensitivity,
            version=latest.version + 1,
            status=status,
            decision=decision,
            conditions=conditions,
            test_references=latest.test_references,
            evidence_references=latest.evidence_references,
            parent_version_id=latest.id,
            change_summary=change_summary,
        )

    def _append_and_mirror(self, artifact: VaultArtifactVersion) -> VaultArtifactVersion:
        stored = self.vault_repository.append_version(artifact)
        self.kernel_repository.append_output(
            OutputArtifact(
                id=stored.id,
                case_id=stored.case_id,
                artifact_type=stored.artifact_type,
                owner_id=stored.owner_id,
                content=stored.to_dict(),
                version=stored.version,
                status=stored.status,
            )
        )
        self.kernel_repository.append_evidence(
            EvidenceReference(
                case_id=stored.case_id,
                label=f"Output Vault artifact {stored.artifact_type} v{stored.version}",
                uri=f"vault://artifacts/{stored.artifact_id}/versions/{stored.version}",
                sensitivity=stored.sensitivity,
            )
        )
        return stored

    @staticmethod
    def _status_for_decision(decision: VaultDecision) -> ArtifactStatus:
        if decision in {VaultDecision.APPROVED, VaultDecision.APPROVED_WITH_CONDITIONS}:
            return ArtifactStatus.APPROVED
        if decision == VaultDecision.REJECTED:
            return ArtifactStatus.REJECTED
        return ArtifactStatus.REVIEW

    @staticmethod
    def _assert_sensitivity_allowed(
        case_sensitivity: Sensitivity,
        artifact_sensitivity: Sensitivity,
    ) -> None:
        order = {
            Sensitivity.GREEN: 0,
            Sensitivity.ORANGE: 1,
            Sensitivity.RED: 2,
        }
        if order[artifact_sensitivity] > order[case_sensitivity]:
            raise VaultApprovalError(
                "Artifact sensitivity cannot exceed the sensitivity declared for the Kernel case"
            )

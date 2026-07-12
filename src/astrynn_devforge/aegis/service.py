from __future__ import annotations

from uuid import UUID

from astrynn_devforge.kernel import (
    ArtifactStatus,
    EvidenceReference,
    KernelRepository,
    OutputArtifact,
)

from .models import (
    AIUseCase,
    ClearancePackage,
    ClearanceProofReceipt,
    ClearanceResult,
)
from .scoring import build_conditions, build_guardrails, determine_decision


class AegisClearanceService:
    """Deterministic Deployment Clearance service.

    The service evaluates and records evidence. It never changes a case to ACTIVE,
    deploys an agent, or grants permissions.
    """

    def evaluate(self, use_case: AIUseCase) -> ClearancePackage:
        decision, reasons = determine_decision(use_case)
        guardrails = build_guardrails(use_case)
        conditions = build_conditions(decision, guardrails)
        dimension_scores = tuple(
            (dimension.value, score)
            for dimension, score in use_case.scores.as_dict().items()
        )

        result = ClearanceResult(
            use_case_id=use_case.id,
            case_id=use_case.case_id,
            decision=decision,
            total_score=use_case.scores.total,
            dimension_scores=dimension_scores,
            reasons=reasons,
            conditions=conditions,
            guardrails=guardrails,
            specialist_triggers=use_case.specialist_triggers,
        )
        receipt = ClearanceProofReceipt(
            clearance_result_id=result.id,
            use_case_id=use_case.id,
            case_id=use_case.case_id,
            input_fingerprint=use_case.fingerprint(),
            decision=result.decision,
            total_score=result.total_score,
            conditions=result.conditions,
            methodology_version=result.methodology_version,
        )
        return ClearancePackage(result=result, receipt=receipt)

    def record(
        self,
        *,
        package: ClearancePackage,
        repository: KernelRepository,
        owner_id: UUID,
    ) -> tuple[OutputArtifact, EvidenceReference]:
        case = repository.get_case(package.result.case_id)
        content = {
            "clearance_result": package.result.to_dict(),
            "proof_receipt": package.receipt.to_dict(),
        }
        output = OutputArtifact(
            case_id=case.id,
            artifact_type="AEGIS_CLEARANCE_REPORT",
            owner_id=owner_id,
            content=content,
            status=ArtifactStatus.REVIEW,
        )
        evidence = EvidenceReference(
            case_id=case.id,
            label="Aegis Clearance Proof Receipt",
            uri=f"aegis://clearance/{package.result.id}",
            sensitivity=case.sensitivity,
        )
        repository.append_output(output)
        repository.append_evidence(evidence)
        return output, evidence

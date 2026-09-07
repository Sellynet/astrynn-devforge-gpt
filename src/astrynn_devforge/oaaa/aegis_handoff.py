from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Any
from uuid import UUID, uuid4

from astrynn_devforge.aegis import (
    AIUseCase,
    ClearanceProofReceipt,
    RiskScores,
    SpecialistReviewTrigger,
)

from .enums import BlueprintStatus
from .repository import AgentBlueprintRepository


HANDOFF_SCHEMA_VERSION = "OAAA-AEGIS-HANDOFF-0.1"
ELIGIBLE_SOURCE_STATUS = BlueprintStatus.IN_REVIEW
_REQUIRED_AEGIS_CONTEXT = ("sector", "scores")
_MAPPED_FIELDS = (
    "case_id->case_id",
    "organization_id->organization_id",
    "owner_id->owner_id",
    "name->title",
    "business_need->purpose",
    "data_boundary.allowed_categories->data_categories",
    "allowed_actions->requested_actions",
)
_UNMAPPED_FIELDS = (
    "role",
    "tools",
    "data_boundary.prohibited_categories",
    "prohibited_actions",
    "approval_points",
    "logs_required",
    "aria_test_plan",
    "rollback_procedure",
    "disable_procedure",
    "sensitivity",
)


def utc_now() -> datetime:
    return datetime.now(UTC)


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class HandoffAcknowledgementState(StrEnum):
    ACCEPTED_FOR_EVALUATION = "ACCEPTED_FOR_EVALUATION"
    REJECTED_INCOMPLETE = "REJECTED_INCOMPLETE"
    REJECTED_IDENTITY_MISMATCH = "REJECTED_IDENTITY_MISMATCH"
    REJECTED_STALE_SOURCE = "REJECTED_STALE_SOURCE"
    REJECTED_SCHEMA_VERSION = "REJECTED_SCHEMA_VERSION"
    REJECTED_UNSUPPORTED_MAPPING = "REJECTED_UNSUPPORTED_MAPPING"


class HandoffRejectedError(ValueError):
    def __init__(self, state: HandoffAcknowledgementState, message: str) -> None:
        super().__init__(message)
        self.state = state


@dataclass(frozen=True, slots=True)
class AegisHandoffContext:
    case_id: UUID
    organization_id: UUID
    owner_id: UUID
    sector: str
    scores: RiskScores | None
    systems: tuple[str, ...] = ()
    users: tuple[str, ...] = ()
    providers: tuple[str, ...] = ()
    specialist_triggers: tuple[SpecialistReviewTrigger, ...] = ()
    critical_blockers: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class OAAAtoAegisClearanceHandoff:
    case_id: UUID
    organization_id: UUID
    owner_id: UUID
    blueprint_id: UUID
    blueprint_version_id: UUID
    blueprint_version: int
    source_status: BlueprintStatus
    source_safety_fingerprint: str
    source_integrity_hash: str
    material_change: bool
    target_use_case_id: UUID
    target_fingerprint: str
    source_evidence_refs: tuple[str, ...]
    supplemental_evidence_refs: tuple[str, ...]
    mapped_fields: tuple[str, ...] = _MAPPED_FIELDS
    unmapped_fields: tuple[str, ...] = _UNMAPPED_FIELDS
    required_aegis_context: tuple[str, ...] = _REQUIRED_AEGIS_CONTEXT
    source_system: str = "ORBYN_OAAA"
    target_system: str = "AEGIS"
    schema_version: str = HANDOFF_SCHEMA_VERSION
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "source_system": self.source_system,
            "target_system": self.target_system,
            "case_id": str(self.case_id),
            "organization_id": str(self.organization_id),
            "owner_id": str(self.owner_id),
            "blueprint_id": str(self.blueprint_id),
            "blueprint_version_id": str(self.blueprint_version_id),
            "blueprint_version": self.blueprint_version,
            "source_status": self.source_status.value,
            "source_safety_fingerprint": self.source_safety_fingerprint,
            "source_integrity_hash": self.source_integrity_hash,
            "material_change": self.material_change,
            "target_use_case_id": str(self.target_use_case_id),
            "target_fingerprint": self.target_fingerprint,
            "mapped_fields": list(self.mapped_fields),
            "unmapped_fields": list(self.unmapped_fields),
            "required_aegis_context": list(self.required_aegis_context),
            "source_evidence_refs": list(self.source_evidence_refs),
            "supplemental_evidence_refs": list(self.supplemental_evidence_refs),
        }

    @property
    def fingerprint(self) -> str:
        return sha256(_canonical_json(self.canonical_payload()).encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            **self.canonical_payload(),
            "handoff_fingerprint": self.fingerprint,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class HandoffAcknowledgement:
    handoff_id: UUID
    state: HandoffAcknowledgementState
    target_use_case_id: UUID
    message: str = "Accepted for Aegis input construction/evaluation only"
    created_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class OAAAtoAegisHandoffResult:
    handoff: OAAAtoAegisClearanceHandoff
    use_case: AIUseCase
    acknowledgement: HandoffAcknowledgement


@dataclass(frozen=True, slots=True)
class HandoffClearanceEvidence:
    handoff_id: UUID
    handoff_fingerprint: str
    source_safety_fingerprint: str
    target_use_case_id: UUID
    target_fingerprint: str
    clearance_result_id: UUID
    clearance_receipt_id: UUID
    clearance_input_fingerprint: str


class OAAAtoAegisHandoffService:
    """Bounded OAAA -> Aegis handoff. It never grants authority or executes actions."""

    def __init__(self, blueprint_repository: AgentBlueprintRepository) -> None:
        self.blueprint_repository = blueprint_repository

    def build(
        self,
        *,
        blueprint_id: UUID,
        expected_source_safety_fingerprint: str,
        context: AegisHandoffContext,
        schema_version: str = HANDOFF_SCHEMA_VERSION,
    ) -> OAAAtoAegisHandoffResult:
        if schema_version != HANDOFF_SCHEMA_VERSION:
            raise HandoffRejectedError(
                HandoffAcknowledgementState.REJECTED_SCHEMA_VERSION,
                f"Unsupported handoff schema version: {schema_version}",
            )

        latest = self.blueprint_repository.latest_version(blueprint_id)
        if latest.status != ELIGIBLE_SOURCE_STATUS:
            raise HandoffRejectedError(
                HandoffAcknowledgementState.REJECTED_UNSUPPORTED_MAPPING,
                "Only an IN_REVIEW blueprint is eligible for the bounded Aegis handoff",
            )
        if expected_source_safety_fingerprint != latest.safety_fingerprint:
            raise HandoffRejectedError(
                HandoffAcknowledgementState.REJECTED_STALE_SOURCE,
                "The source blueprint safety fingerprint is stale",
            )
        if (
            context.case_id != latest.case_id
            or context.organization_id != latest.organization_id
            or context.owner_id != latest.owner_id
        ):
            raise HandoffRejectedError(
                HandoffAcknowledgementState.REJECTED_IDENTITY_MISMATCH,
                "Aegis supplemental identity must exactly match the OAAA source identity",
            )
        if latest.vault_artifact_id is None:
            raise HandoffRejectedError(
                HandoffAcknowledgementState.REJECTED_INCOMPLETE,
                "The source blueprint has no Output Vault artifact reference",
            )
        if not context.sector.strip():
            raise HandoffRejectedError(
                HandoffAcknowledgementState.REJECTED_INCOMPLETE,
                "Aegis sector is required and cannot be inferred from OAAA",
            )
        if context.scores is None:
            raise HandoffRejectedError(
                HandoffAcknowledgementState.REJECTED_INCOMPLETE,
                "Complete Aegis RiskScores are required and cannot be inferred from OAAA",
            )
        if not context.evidence_refs or any(not ref.strip() for ref in context.evidence_refs):
            raise HandoffRejectedError(
                HandoffAcknowledgementState.REJECTED_INCOMPLETE,
                "Aegis supplemental context requires at least one evidence reference",
            )
        if any(not blocker.strip() for blocker in context.critical_blockers):
            raise HandoffRejectedError(
                HandoffAcknowledgementState.REJECTED_INCOMPLETE,
                "Aegis critical blockers cannot contain blank values",
            )

        use_case = AIUseCase(
            case_id=latest.case_id,
            organization_id=latest.organization_id,
            owner_id=latest.owner_id,
            title=latest.name,
            purpose=latest.business_need,
            sector=context.sector,
            scores=context.scores,
            data_categories=latest.data_boundary.allowed_categories,
            systems=context.systems,
            users=context.users,
            requested_actions=latest.allowed_actions,
            providers=context.providers,
            specialist_triggers=context.specialist_triggers,
            critical_blockers=context.critical_blockers,
        )

        source_evidence_refs = (
            f"oaaa://blueprints/{latest.blueprint_id}/versions/{latest.version}",
            f"vault://artifacts/{latest.vault_artifact_id}",
        )
        handoff = OAAAtoAegisClearanceHandoff(
            case_id=latest.case_id,
            organization_id=latest.organization_id,
            owner_id=latest.owner_id,
            blueprint_id=latest.blueprint_id,
            blueprint_version_id=latest.id,
            blueprint_version=latest.version,
            source_status=latest.status,
            source_safety_fingerprint=latest.safety_fingerprint,
            source_integrity_hash=latest.integrity_hash,
            material_change=latest.material_change,
            target_use_case_id=use_case.id,
            target_fingerprint=use_case.fingerprint(),
            source_evidence_refs=source_evidence_refs,
            supplemental_evidence_refs=context.evidence_refs,
        )
        acknowledgement = HandoffAcknowledgement(
            handoff_id=handoff.id,
            state=HandoffAcknowledgementState.ACCEPTED_FOR_EVALUATION,
            target_use_case_id=use_case.id,
        )
        return OAAAtoAegisHandoffResult(
            handoff=handoff,
            use_case=use_case,
            acknowledgement=acknowledgement,
        )

    def bind_clearance_receipt(
        self,
        *,
        result: OAAAtoAegisHandoffResult,
        receipt: ClearanceProofReceipt,
    ) -> HandoffClearanceEvidence:
        latest = self.blueprint_repository.latest_version(result.handoff.blueprint_id)
        if latest.safety_fingerprint != result.handoff.source_safety_fingerprint:
            raise HandoffRejectedError(
                HandoffAcknowledgementState.REJECTED_STALE_SOURCE,
                "A clearance receipt cannot satisfy a changed blueprint fingerprint",
            )
        target_fingerprint = result.use_case.fingerprint()
        if (
            result.use_case.id != result.handoff.target_use_case_id
            or target_fingerprint != result.handoff.target_fingerprint
        ):
            raise HandoffRejectedError(
                HandoffAcknowledgementState.REJECTED_UNSUPPORTED_MAPPING,
                "The target AIUseCase no longer matches the handoff evidence",
            )
        if (
            receipt.use_case_id != result.use_case.id
            or receipt.case_id != result.use_case.case_id
            or receipt.input_fingerprint != target_fingerprint
        ):
            raise HandoffRejectedError(
                HandoffAcknowledgementState.REJECTED_UNSUPPORTED_MAPPING,
                "The Aegis Clearance receipt does not match the handed-off AIUseCase",
            )
        return HandoffClearanceEvidence(
            handoff_id=result.handoff.id,
            handoff_fingerprint=result.handoff.fingerprint,
            source_safety_fingerprint=result.handoff.source_safety_fingerprint,
            target_use_case_id=result.use_case.id,
            target_fingerprint=target_fingerprint,
            clearance_result_id=receipt.clearance_result_id,
            clearance_receipt_id=receipt.id,
            clearance_input_fingerprint=receipt.input_fingerprint,
        )

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256
import json
from typing import Any
from uuid import UUID, uuid4

from .enums import (
    ClearanceDecision,
    GuardrailPriority,
    RiskDimension,
    SpecialistReviewTrigger,
)


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class RiskScores:
    data: int
    permissions: int
    autonomy: int
    impact: int
    traceability: int
    human_oversight: int
    external_dependency: int
    adversarial_robustness: int
    incident_readiness: int

    def __post_init__(self) -> None:
        for dimension, score in self.as_dict().items():
            if isinstance(score, bool) or not isinstance(score, int):
                raise TypeError(f"{dimension.value} score must be an integer")
            if score < 0 or score > 5:
                raise ValueError(f"{dimension.value} score must be between 0 and 5")

    def as_dict(self) -> dict[RiskDimension, int]:
        return {
            RiskDimension.DATA: self.data,
            RiskDimension.PERMISSIONS: self.permissions,
            RiskDimension.AUTONOMY: self.autonomy,
            RiskDimension.IMPACT: self.impact,
            RiskDimension.TRACEABILITY: self.traceability,
            RiskDimension.HUMAN_OVERSIGHT: self.human_oversight,
            RiskDimension.EXTERNAL_DEPENDENCY: self.external_dependency,
            RiskDimension.ADVERSARIAL_ROBUSTNESS: self.adversarial_robustness,
            RiskDimension.INCIDENT_READINESS: self.incident_readiness,
        }

    @property
    def total(self) -> int:
        return sum(self.as_dict().values())


@dataclass(frozen=True, slots=True)
class AIUseCase:
    case_id: UUID
    organization_id: UUID
    owner_id: UUID
    title: str
    purpose: str
    sector: str
    scores: RiskScores
    data_categories: tuple[str, ...] = ()
    systems: tuple[str, ...] = ()
    users: tuple[str, ...] = ()
    requested_actions: tuple[str, ...] = ()
    providers: tuple[str, ...] = ()
    specialist_triggers: tuple[SpecialistReviewTrigger, ...] = ()
    critical_blockers: tuple[str, ...] = ()
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Use-case title is required")
        if not self.purpose.strip():
            raise ValueError("Use-case purpose is required")
        if not self.sector.strip():
            raise ValueError("Use-case sector is required")
        for blocker in self.critical_blockers:
            if not blocker.strip():
                raise ValueError("Critical blockers cannot be blank")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "case_id": str(self.case_id),
            "organization_id": str(self.organization_id),
            "owner_id": str(self.owner_id),
            "title": self.title.strip(),
            "purpose": self.purpose.strip(),
            "sector": self.sector.strip(),
            "scores": {
                dimension.value: score
                for dimension, score in self.scores.as_dict().items()
            },
            "data_categories": list(self.data_categories),
            "systems": list(self.systems),
            "users": list(self.users),
            "requested_actions": list(self.requested_actions),
            "providers": list(self.providers),
            "specialist_triggers": [trigger.value for trigger in self.specialist_triggers],
            "critical_blockers": list(self.critical_blockers),
        }

    def fingerprint(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(), sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        return sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class GuardrailRecommendation:
    code: str
    title: str
    rationale: str
    dimensions: tuple[RiskDimension, ...]
    priority: GuardrailPriority


@dataclass(frozen=True, slots=True)
class ClearanceResult:
    use_case_id: UUID
    case_id: UUID
    decision: ClearanceDecision
    total_score: int
    dimension_scores: tuple[tuple[str, int], ...]
    reasons: tuple[str, ...]
    conditions: tuple[str, ...]
    guardrails: tuple[GuardrailRecommendation, ...]
    specialist_triggers: tuple[SpecialistReviewTrigger, ...]
    methodology_version: str = "AEGIS-CLEARANCE-0.1"
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "use_case_id": str(self.use_case_id),
            "case_id": str(self.case_id),
            "decision": self.decision.value,
            "total_score": self.total_score,
            "dimension_scores": dict(self.dimension_scores),
            "reasons": list(self.reasons),
            "conditions": list(self.conditions),
            "guardrails": [
                {
                    "code": item.code,
                    "title": item.title,
                    "rationale": item.rationale,
                    "dimensions": [dimension.value for dimension in item.dimensions],
                    "priority": item.priority.value,
                }
                for item in self.guardrails
            ],
            "specialist_triggers": [item.value for item in self.specialist_triggers],
            "methodology_version": self.methodology_version,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class ClearanceProofReceipt:
    clearance_result_id: UUID
    use_case_id: UUID
    case_id: UUID
    input_fingerprint: str
    decision: ClearanceDecision
    total_score: int
    conditions: tuple[str, ...]
    methodology_version: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "clearance_result_id": str(self.clearance_result_id),
            "use_case_id": str(self.use_case_id),
            "case_id": str(self.case_id),
            "input_fingerprint": self.input_fingerprint,
            "decision": self.decision.value,
            "total_score": self.total_score,
            "conditions": list(self.conditions),
            "methodology_version": self.methodology_version,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class ClearancePackage:
    result: ClearanceResult
    receipt: ClearanceProofReceipt

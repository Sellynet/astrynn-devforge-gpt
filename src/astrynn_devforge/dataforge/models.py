from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256
import json
from typing import Any
from uuid import UUID, uuid4

from astrynn_devforge.kernel import ArtifactStatus, Sensitivity

from .enums import VaultDecision


def utc_now() -> datetime:
    return datetime.now(UTC)


def _require_text(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True, slots=True)
class VaultArtifactVersion:
    artifact_id: UUID
    case_id: UUID
    owner_id: UUID
    created_by: UUID
    artifact_type: str
    title: str
    content: dict[str, Any]
    sensitivity: Sensitivity
    version: int
    status: ArtifactStatus
    decision: VaultDecision | None = None
    conditions: tuple[str, ...] = ()
    test_references: tuple[str, ...] = ()
    evidence_references: tuple[str, ...] = ()
    parent_version_id: UUID | None = None
    change_summary: str = ""
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _require_text(self.artifact_type, "Artifact type")
        _require_text(self.title, "Artifact title")
        if self.version < 1:
            raise ValueError("Artifact version must be at least 1")
        if not isinstance(self.content, dict):
            raise TypeError("Artifact content must be a dictionary")
        for reference in (*self.test_references, *self.evidence_references):
            _require_text(reference, "Reference")
        for condition in self.conditions:
            _require_text(condition, "Condition")
        if self.status in {ArtifactStatus.APPROVED, ArtifactStatus.REJECTED} and self.decision is None:
            raise ValueError("Approved or rejected artifacts require a decision")
        if self.decision == VaultDecision.APPROVED_WITH_CONDITIONS and not self.conditions:
            raise ValueError("Conditional approval requires at least one condition")

    def integrity_payload(self) -> dict[str, Any]:
        return {
            "artifact_type": self.artifact_type.strip(),
            "title": self.title.strip(),
            "content": self.content,
            "sensitivity": self.sensitivity.value,
            "status": self.status.value,
            "decision": self.decision.value if self.decision else None,
            "conditions": list(self.conditions),
            "test_references": list(self.test_references),
            "evidence_references": list(self.evidence_references),
            "change_summary": self.change_summary.strip(),
        }

    @property
    def integrity_hash(self) -> str:
        return sha256(_canonical_json(self.integrity_payload()).encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "artifact_id": str(self.artifact_id),
            "case_id": str(self.case_id),
            "owner_id": str(self.owner_id),
            "created_by": str(self.created_by),
            "artifact_type": self.artifact_type,
            "title": self.title,
            "content": self.content,
            "sensitivity": self.sensitivity.value,
            "version": self.version,
            "status": self.status.value,
            "decision": self.decision.value if self.decision else None,
            "conditions": list(self.conditions),
            "test_references": list(self.test_references),
            "evidence_references": list(self.evidence_references),
            "parent_version_id": str(self.parent_version_id) if self.parent_version_id else None,
            "change_summary": self.change_summary,
            "integrity_hash": self.integrity_hash,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class VaultProofReceipt:
    artifact_id: UUID
    artifact_version_id: UUID
    case_id: UUID
    version: int
    evaluator_id: UUID
    decision: VaultDecision
    conditions: tuple[str, ...]
    test_references: tuple[str, ...]
    evidence_references: tuple[str, ...]
    artifact_integrity_hash: str
    methodology_version: str = "OUTPUT-VAULT-0.1"
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if self.version < 1:
            raise ValueError("Receipt version must be at least 1")
        _require_text(self.artifact_integrity_hash, "Artifact integrity hash")
        _require_text(self.methodology_version, "Methodology version")
        if self.decision == VaultDecision.APPROVED_WITH_CONDITIONS and not self.conditions:
            raise ValueError("Conditional approval requires at least one condition")

    def integrity_payload(self) -> dict[str, Any]:
        return {
            "artifact_id": str(self.artifact_id),
            "artifact_version_id": str(self.artifact_version_id),
            "case_id": str(self.case_id),
            "version": self.version,
            "evaluator_id": str(self.evaluator_id),
            "decision": self.decision.value,
            "conditions": list(self.conditions),
            "test_references": list(self.test_references),
            "evidence_references": list(self.evidence_references),
            "artifact_integrity_hash": self.artifact_integrity_hash,
            "methodology_version": self.methodology_version,
        }

    @property
    def receipt_hash(self) -> str:
        return sha256(_canonical_json(self.integrity_payload()).encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            **self.integrity_payload(),
            "receipt_hash": self.receipt_hash,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class VaultDecisionPackage:
    artifact: VaultArtifactVersion
    receipt: VaultProofReceipt

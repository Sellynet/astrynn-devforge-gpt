from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256
import json
from typing import Any
from uuid import UUID, uuid4

from astrynn_devforge.kernel import Sensitivity
from astrynn_devforge.oaaa.enums import ARIATestFamily

from .enums import (
    ARIAFindingDisposition,
    ARIAFindingSeverity,
    ARIATestOutcome,
    ARIAVerdict,
)


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
class ARIAFindingInput:
    severity: ARIAFindingSeverity
    title: str
    description: str
    remediation: str

    def __post_init__(self) -> None:
        _require_text(self.title, "Finding title")
        _require_text(self.description, "Finding description")
        _require_text(self.remediation, "Finding remediation")


@dataclass(frozen=True, slots=True)
class ARIACampaign:
    case_id: UUID
    blueprint_id: UUID
    blueprint_version_id: UUID
    blueprint_fingerprint: str
    owner_id: UUID
    created_by: UUID
    required_families: tuple[ARIATestFamily, ...]
    sensitivity: Sensitivity
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _require_text(self.blueprint_fingerprint, "Blueprint fingerprint")
        if not self.required_families:
            raise ValueError("An ARIA campaign requires at least one test family")
        if len(set(self.required_families)) != len(self.required_families):
            raise ValueError("ARIA campaign test families must be unique")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "case_id": str(self.case_id),
            "blueprint_id": str(self.blueprint_id),
            "blueprint_version_id": str(self.blueprint_version_id),
            "blueprint_fingerprint": self.blueprint_fingerprint,
            "owner_id": str(self.owner_id),
            "created_by": str(self.created_by),
            "required_families": [item.value for item in self.required_families],
            "sensitivity": self.sensitivity.value,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class ARIATestRecord:
    campaign_id: UUID
    case_id: UUID
    blueprint_id: UUID
    blueprint_version_id: UUID
    blueprint_fingerprint: str
    family: ARIATestFamily
    objective: str
    adversarial_input: str
    expected_behavior: str
    actual_behavior: str
    outcome: ARIATestOutcome
    executed_by: UUID
    evidence_references: tuple[str, ...]
    run_number: int
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _require_text(self.blueprint_fingerprint, "Blueprint fingerprint")
        _require_text(self.objective, "Test objective")
        _require_text(self.adversarial_input, "Adversarial input")
        _require_text(self.expected_behavior, "Expected behavior")
        _require_text(self.actual_behavior, "Actual behavior")
        if self.run_number < 1:
            raise ValueError("ARIA run number must be at least 1")
        if not self.evidence_references:
            raise ValueError("An ARIA test requires at least one evidence reference")
        for reference in self.evidence_references:
            _require_text(reference, "Evidence reference")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "campaign_id": str(self.campaign_id),
            "case_id": str(self.case_id),
            "blueprint_id": str(self.blueprint_id),
            "blueprint_version_id": str(self.blueprint_version_id),
            "blueprint_fingerprint": self.blueprint_fingerprint,
            "family": self.family.value,
            "objective": self.objective.strip(),
            "adversarial_input": self.adversarial_input,
            "expected_behavior": self.expected_behavior.strip(),
            "actual_behavior": self.actual_behavior.strip(),
            "outcome": self.outcome.value,
            "executed_by": str(self.executed_by),
            "evidence_references": list(self.evidence_references),
            "run_number": self.run_number,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class ARIAFinding:
    campaign_id: UUID
    test_record_id: UUID
    severity: ARIAFindingSeverity
    title: str
    description: str
    remediation: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _require_text(self.title, "Finding title")
        _require_text(self.description, "Finding description")
        _require_text(self.remediation, "Finding remediation")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "campaign_id": str(self.campaign_id),
            "test_record_id": str(self.test_record_id),
            "severity": self.severity.value,
            "title": self.title.strip(),
            "description": self.description.strip(),
            "remediation": self.remediation.strip(),
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class ARIAFindingResolution:
    finding_id: UUID
    disposition: ARIAFindingDisposition
    resolved_by: UUID
    rationale: str
    evidence_references: tuple[str, ...]
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _require_text(self.rationale, "Resolution rationale")
        if not self.evidence_references:
            raise ValueError("A finding resolution requires evidence")
        for reference in self.evidence_references:
            _require_text(reference, "Evidence reference")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "finding_id": str(self.finding_id),
            "disposition": self.disposition.value,
            "resolved_by": str(self.resolved_by),
            "rationale": self.rationale.strip(),
            "evidence_references": list(self.evidence_references),
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class ARIAReceipt:
    campaign_id: UUID
    case_id: UUID
    blueprint_id: UUID
    blueprint_version_id: UUID
    blueprint_fingerprint: str
    verdict: ARIAVerdict
    latest_test_record_ids: tuple[UUID, ...]
    finding_ids: tuple[UUID, ...]
    open_finding_ids: tuple[UUID, ...]
    unresolved_critical_findings: int
    unresolved_high_findings: int
    evidence_references: tuple[str, ...]
    finalized_by: UUID
    version: int
    methodology_version: str = "ARIA-TEST-REGISTER-0.1"
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _require_text(self.blueprint_fingerprint, "Blueprint fingerprint")
        _require_text(self.methodology_version, "Methodology version")
        if self.version < 1:
            raise ValueError("ARIA receipt version must be at least 1")
        if self.unresolved_critical_findings < 0 or self.unresolved_high_findings < 0:
            raise ValueError("Unresolved finding counts cannot be negative")
        if self.verdict != ARIAVerdict.BLOCKED and self.unresolved_critical_findings:
            raise ValueError("A non-blocked ARIA receipt cannot contain open critical findings")

    def integrity_payload(self) -> dict[str, Any]:
        return {
            "campaign_id": str(self.campaign_id),
            "case_id": str(self.case_id),
            "blueprint_id": str(self.blueprint_id),
            "blueprint_version_id": str(self.blueprint_version_id),
            "blueprint_fingerprint": self.blueprint_fingerprint,
            "verdict": self.verdict.value,
            "latest_test_record_ids": [str(item) for item in self.latest_test_record_ids],
            "finding_ids": [str(item) for item in self.finding_ids],
            "open_finding_ids": [str(item) for item in self.open_finding_ids],
            "unresolved_critical_findings": self.unresolved_critical_findings,
            "unresolved_high_findings": self.unresolved_high_findings,
            "evidence_references": list(self.evidence_references),
            "finalized_by": str(self.finalized_by),
            "version": self.version,
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

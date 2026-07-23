from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any
from uuid import UUID, uuid4

from astrynn_devforge.kernel import Sensitivity

from .enums import RiskLevel, ScenarioType, SourceKind, StatementType


def utc_now() -> datetime:
    return datetime.now(UTC)


def _require_text(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


def _validate_range(value: int, field_name: str, minimum: int, maximum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer")
    if value < minimum or value > maximum:
        raise ValueError(f"{field_name} must be between {minimum} and {maximum}")


@dataclass(frozen=True, slots=True)
class AtlasCaseInput:
    case_id: UUID
    organization_id: UUID
    owner_id: UUID
    title: str
    problem: str
    sector: str
    country: str
    horizon_days: int
    asset: str | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _require_text(self.title, "Atlas case title")
        _require_text(self.problem, "Operational problem")
        _require_text(self.sector, "Sector")
        _require_text(self.country, "Country")
        if self.horizon_days <= 0:
            raise ValueError("horizon_days must be greater than zero")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "case_id": str(self.case_id),
            "organization_id": str(self.organization_id),
            "owner_id": str(self.owner_id),
            "title": self.title.strip(),
            "problem": self.problem.strip(),
            "sector": self.sector.strip(),
            "country": self.country.strip(),
            "horizon_days": self.horizon_days,
            "asset": self.asset.strip() if self.asset else None,
        }


@dataclass(frozen=True, slots=True)
class AtlasSource:
    case_id: UUID
    title: str
    kind: SourceKind
    confidence: int
    sensitivity: Sensitivity
    uri: str | None = None
    notes: str = ""
    id: UUID = field(default_factory=uuid4)
    captured_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _require_text(self.title, "Source title")
        _validate_range(self.confidence, "Source confidence", 0, 100)
        if self.uri is not None and not self.uri.strip():
            raise ValueError("Source URI cannot be blank")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "case_id": str(self.case_id),
            "title": self.title.strip(),
            "kind": self.kind.value,
            "confidence": self.confidence,
            "sensitivity": self.sensitivity.value,
            "uri": self.uri.strip() if self.uri else None,
            "notes": self.notes.strip(),
        }


@dataclass(frozen=True, slots=True)
class AtlasSignal:
    case_id: UUID
    title: str
    observation: str
    source_ids: tuple[UUID, ...]
    confidence: int
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _require_text(self.title, "Signal title")
        _require_text(self.observation, "Signal observation")
        _validate_range(self.confidence, "Signal confidence", 0, 100)
        if not self.source_ids:
            raise ValueError("A signal requires at least one source")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "case_id": str(self.case_id),
            "title": self.title.strip(),
            "observation": self.observation.strip(),
            "source_ids": sorted(str(item) for item in self.source_ids),
            "confidence": self.confidence,
        }


@dataclass(frozen=True, slots=True)
class AtlasRisk:
    case_id: UUID
    title: str
    description: str
    probability: int
    impact: int
    related_signal_ids: tuple[UUID, ...]
    mitigation: str = ""
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _require_text(self.title, "Risk title")
        _require_text(self.description, "Risk description")
        _validate_range(self.probability, "Risk probability", 1, 5)
        _validate_range(self.impact, "Risk impact", 1, 5)
        if not self.related_signal_ids:
            raise ValueError("A risk requires at least one related signal")

    @property
    def severity(self) -> int:
        return self.probability * self.impact

    @property
    def level(self) -> RiskLevel:
        if self.severity >= 20:
            return RiskLevel.CRITICAL
        if self.severity >= 12:
            return RiskLevel.HIGH
        if self.severity >= 6:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "case_id": str(self.case_id),
            "title": self.title.strip(),
            "description": self.description.strip(),
            "probability": self.probability,
            "impact": self.impact,
            "severity": self.severity,
            "level": self.level.value,
            "related_signal_ids": sorted(str(item) for item in self.related_signal_ids),
            "mitigation": self.mitigation.strip(),
        }


@dataclass(frozen=True, slots=True)
class AtlasScenario:
    case_id: UUID
    scenario_type: ScenarioType
    title: str
    narrative: str
    assumptions: tuple[str, ...]
    early_indicators: tuple[str, ...]
    response_options: tuple[str, ...]
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _require_text(self.title, "Scenario title")
        _require_text(self.narrative, "Scenario narrative")
        if not self.assumptions:
            raise ValueError("A scenario requires at least one assumption")
        if not self.early_indicators:
            raise ValueError("A scenario requires at least one early indicator")
        if not self.response_options:
            raise ValueError("A scenario requires at least one response option")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "case_id": str(self.case_id),
            "scenario_type": self.scenario_type.value,
            "title": self.title.strip(),
            "narrative": self.narrative.strip(),
            "assumptions": [item.strip() for item in self.assumptions],
            "early_indicators": [item.strip() for item in self.early_indicators],
            "response_options": [item.strip() for item in self.response_options],
        }


@dataclass(frozen=True, slots=True)
class AtlasStakeholder:
    case_id: UUID
    name: str
    role: str
    influence: int
    exposure: int
    interests: tuple[str, ...]
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _require_text(self.name, "Stakeholder name")
        _require_text(self.role, "Stakeholder role")
        _validate_range(self.influence, "Stakeholder influence", 1, 5)
        _validate_range(self.exposure, "Stakeholder exposure", 1, 5)

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "case_id": str(self.case_id),
            "name": self.name.strip(),
            "role": self.role.strip(),
            "influence": self.influence,
            "exposure": self.exposure,
            "interests": [item.strip() for item in self.interests],
        }


@dataclass(frozen=True, slots=True)
class AtlasStatement:
    statement_type: StatementType
    text: str
    source_ids: tuple[UUID, ...] = ()
    rationale: str = ""

    def __post_init__(self) -> None:
        _require_text(self.text, "Statement text")
        if self.statement_type == StatementType.FACT and not self.source_ids:
            raise ValueError("Facts require at least one source reference")

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.statement_type.value,
            "text": self.text.strip(),
            "source_ids": [str(item) for item in self.source_ids],
            "rationale": self.rationale.strip(),
        }


@dataclass(frozen=True, slots=True)
class AtlasBriefing:
    case_id: UUID
    title: str
    executive_summary: str
    facts: tuple[AtlasStatement, ...]
    inferences: tuple[AtlasStatement, ...]
    assumptions: tuple[AtlasStatement, ...]
    recommendations: tuple[AtlasStatement, ...]
    top_risk_ids: tuple[UUID, ...]
    scenario_ids: tuple[UUID, ...]
    stakeholder_ids: tuple[UUID, ...]
    source_ids: tuple[UUID, ...]
    input_fingerprint: str
    methodology_version: str = "ORBYN-ATLAS-0.1"
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "case_id": str(self.case_id),
            "title": self.title,
            "executive_summary": self.executive_summary,
            "facts": [item.to_dict() for item in self.facts],
            "inferences": [item.to_dict() for item in self.inferences],
            "assumptions": [item.to_dict() for item in self.assumptions],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "top_risk_ids": [str(item) for item in self.top_risk_ids],
            "scenario_ids": [str(item) for item in self.scenario_ids],
            "stakeholder_ids": [str(item) for item in self.stakeholder_ids],
            "source_ids": [str(item) for item in self.source_ids],
            "input_fingerprint": self.input_fingerprint,
            "methodology_version": self.methodology_version,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class AtlasProofReceipt:
    case_id: UUID
    briefing_id: UUID
    input_fingerprint: str
    source_ids: tuple[UUID, ...]
    risk_ids: tuple[UUID, ...]
    scenario_types: tuple[ScenarioType, ...]
    methodology_version: str = "ORBYN-ATLAS-0.1"
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "case_id": str(self.case_id),
            "briefing_id": str(self.briefing_id),
            "input_fingerprint": self.input_fingerprint,
            "source_ids": [str(item) for item in self.source_ids],
            "risk_ids": [str(item) for item in self.risk_ids],
            "scenario_types": [item.value for item in self.scenario_types],
            "methodology_version": self.methodology_version,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class AtlasPackage:
    briefing: AtlasBriefing
    receipt: AtlasProofReceipt


def fingerprint_payload(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import Field, model_validator

from astrynn_devforge.atlas import ScenarioType, SourceKind
from astrynn_devforge.kernel import Sensitivity

from .schemas import APIModel


class AtlasCaseInputRequest(APIModel):
    title: str = Field(min_length=1, max_length=200)
    problem: str = Field(min_length=1, max_length=3000)
    sector: str = Field(min_length=1, max_length=200)
    country: str = Field(min_length=1, max_length=120)
    horizon_days: int = Field(gt=0, le=3650)
    asset: str | None = Field(default=None, max_length=300)


class AtlasSourceRequest(APIModel):
    id: UUID
    title: str = Field(min_length=1, max_length=300)
    kind: SourceKind
    confidence: int = Field(ge=0, le=100)
    sensitivity: Sensitivity
    uri: str | None = Field(default=None, max_length=2000)
    notes: str = Field(default="", max_length=3000)


class AtlasSignalRequest(APIModel):
    id: UUID
    title: str = Field(min_length=1, max_length=300)
    observation: str = Field(min_length=1, max_length=5000)
    source_ids: tuple[UUID, ...] = Field(min_length=1)
    confidence: int = Field(ge=0, le=100)


class AtlasRiskRequest(APIModel):
    id: UUID
    title: str = Field(min_length=1, max_length=300)
    description: str = Field(min_length=1, max_length=5000)
    probability: int = Field(ge=1, le=5)
    impact: int = Field(ge=1, le=5)
    related_signal_ids: tuple[UUID, ...] = Field(min_length=1)
    mitigation: str = Field(default="", max_length=5000)


class AtlasStakeholderRequest(APIModel):
    id: UUID
    name: str = Field(min_length=1, max_length=300)
    role: str = Field(min_length=1, max_length=300)
    influence: int = Field(ge=1, le=5)
    exposure: int = Field(ge=1, le=5)
    interests: tuple[str, ...] = ()


class AtlasScenarioRequest(APIModel):
    id: UUID
    scenario_type: ScenarioType
    title: str = Field(min_length=1, max_length=300)
    narrative: str = Field(min_length=1, max_length=10000)
    assumptions: tuple[str, ...] = Field(min_length=1)
    early_indicators: tuple[str, ...] = Field(min_length=1)
    response_options: tuple[str, ...] = Field(min_length=1)


class AtlasBriefingRequest(APIModel):
    case_input: AtlasCaseInputRequest
    sources: tuple[AtlasSourceRequest, ...] = Field(min_length=1)
    signals: tuple[AtlasSignalRequest, ...] = Field(min_length=1)
    risks: tuple[AtlasRiskRequest, ...] = Field(min_length=1)
    stakeholders: tuple[AtlasStakeholderRequest, ...] = Field(min_length=1)
    scenarios: tuple[AtlasScenarioRequest, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_ids(self) -> AtlasBriefingRequest:
        collections = {
            "source": self.sources,
            "signal": self.signals,
            "risk": self.risks,
            "stakeholder": self.stakeholders,
            "scenario": self.scenarios,
        }
        for label, items in collections.items():
            ids = [item.id for item in items]
            if len(ids) != len(set(ids)):
                raise ValueError(f"Duplicate {label} IDs are not allowed")
        return self


class AtlasPackageResponse(APIModel):
    briefing: dict[str, Any]
    receipt: dict[str, Any]


class RecordedAtlasBriefingResponse(APIModel):
    package: AtlasPackageResponse
    output_id: UUID
    evidence_id: UUID
    artifact_status: str

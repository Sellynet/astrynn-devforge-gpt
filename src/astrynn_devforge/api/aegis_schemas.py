from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import Field

from astrynn_devforge.aegis import SpecialistReviewTrigger

from .schemas import APIModel


class RiskScoresRequest(APIModel):
    data: int = Field(ge=0, le=5)
    permissions: int = Field(ge=0, le=5)
    autonomy: int = Field(ge=0, le=5)
    impact: int = Field(ge=0, le=5)
    traceability: int = Field(ge=0, le=5)
    human_oversight: int = Field(ge=0, le=5)
    external_dependency: int = Field(ge=0, le=5)
    adversarial_robustness: int = Field(ge=0, le=5)
    incident_readiness: int = Field(ge=0, le=5)


class AegisClearanceRequest(APIModel):
    title: str = Field(min_length=1, max_length=200)
    purpose: str = Field(min_length=1, max_length=3000)
    sector: str = Field(min_length=1, max_length=200)
    scores: RiskScoresRequest
    data_categories: tuple[str, ...] = ()
    systems: tuple[str, ...] = ()
    users: tuple[str, ...] = ()
    requested_actions: tuple[str, ...] = ()
    providers: tuple[str, ...] = ()
    specialist_triggers: tuple[SpecialistReviewTrigger, ...] = ()
    critical_blockers: tuple[str, ...] = ()


class ClearancePackageResponse(APIModel):
    result: dict[str, Any]
    receipt: dict[str, Any]


class RecordedClearanceResponse(APIModel):
    package: ClearancePackageResponse
    output_id: UUID
    evidence_id: UUID
    artifact_status: str

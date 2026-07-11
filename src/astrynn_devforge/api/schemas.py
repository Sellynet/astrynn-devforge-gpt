from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from astrynn_devforge.kernel import (
    ApprovalDecision,
    ApprovalRecord,
    Case,
    CaseStatus,
    Sensitivity,
)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=False)


class HealthResponse(StrictModel):
    status: str
    service: str
    version: str
    environment: str
    persistence: str
    external_actions_enabled: bool


class ModuleStatus(StrictModel):
    name: str
    status: str
    evidence: str


class SystemStatusResponse(StrictModel):
    service: str
    version: str
    persistence: str
    modules: list[ModuleStatus]
    counts: dict[str, int]
    external_actions_enabled: bool


class CaseEventResponse(StrictModel):
    id: UUID
    event_type: str
    actor_id: UUID
    details: dict[str, Any]
    created_at: datetime


class CaseResponse(StrictModel):
    id: UUID
    title: str
    description: str
    owner_id: UUID
    organization_id: UUID
    sensitivity: Sensitivity
    status: CaseStatus
    version: int
    created_at: datetime
    updated_at: datetime
    events: list[CaseEventResponse]

    @classmethod
    def from_domain(cls, case: Case) -> "CaseResponse":
        return cls(
            id=case.id,
            title=case.title,
            description=case.description,
            owner_id=case.owner_id,
            organization_id=case.organization_id,
            sensitivity=case.sensitivity,
            status=case.status,
            version=case.version,
            created_at=case.created_at,
            updated_at=case.updated_at,
            events=[
                CaseEventResponse(
                    id=event.id,
                    event_type=event.event_type,
                    actor_id=event.actor_id,
                    details=event.details,
                    created_at=event.created_at,
                )
                for event in case.events
            ],
        )


class CaseCreateRequest(StrictModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)
    owner_id: UUID
    organization_id: UUID
    actor_id: UUID
    sensitivity: Sensitivity = Sensitivity.GREEN


class ApprovalCreateRequest(StrictModel):
    approver_id: UUID
    decision: ApprovalDecision
    rationale: str = Field(min_length=1, max_length=5000)
    conditions: tuple[str, ...] = ()


class ApprovalResponse(StrictModel):
    id: UUID
    case_id: UUID
    approver_id: UUID
    decision: ApprovalDecision
    rationale: str
    conditions: tuple[str, ...]
    created_at: datetime

    @classmethod
    def from_domain(cls, approval: ApprovalRecord) -> "ApprovalResponse":
        return cls(
            id=approval.id,
            case_id=approval.case_id,
            approver_id=approval.approver_id,
            decision=approval.decision,
            rationale=approval.rationale,
            conditions=approval.conditions,
            created_at=approval.created_at,
        )


class TransitionRequest(StrictModel):
    target: CaseStatus
    actor_id: UUID
    reason: str = Field(min_length=1, max_length=2000)


class ErrorDetail(StrictModel):
    code: str
    message: str
    request_id: str | None = None


class ErrorResponse(StrictModel):
    error: ErrorDetail

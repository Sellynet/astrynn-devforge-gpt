from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from astrynn_devforge.kernel import ApprovalDecision, CaseStatus, Sensitivity


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "astrynn-devforge"
    version: str = "0.1.0"
    persistence: str = "in-memory-development"


class CaseCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)
    owner_id: UUID
    organization_id: UUID
    sensitivity: Sensitivity
    actor_id: UUID


class CaseTransitionRequest(BaseModel):
    target: CaseStatus
    actor_id: UUID
    reason: str = Field(min_length=1, max_length=1000)


class ApprovalCreateRequest(BaseModel):
    approver_id: UUID
    decision: ApprovalDecision
    rationale: str = Field(min_length=1, max_length=2000)
    conditions: tuple[str, ...] = ()


class CaseEventResponse(BaseModel):
    event_type: str
    actor_id: UUID
    details: dict[str, object]
    created_at: datetime


class CaseResponse(BaseModel):
    id: UUID
    title: str
    description: str
    owner_id: UUID
    organization_id: UUID
    sensitivity: Sensitivity
    status: CaseStatus
    created_at: datetime
    updated_at: datetime
    events: tuple[CaseEventResponse, ...]


class ApprovalResponse(BaseModel):
    id: UUID
    case_id: UUID
    approver_id: UUID
    decision: ApprovalDecision
    rationale: str
    conditions: tuple[str, ...]
    created_at: datetime


class ErrorResponse(BaseModel):
    detail: str

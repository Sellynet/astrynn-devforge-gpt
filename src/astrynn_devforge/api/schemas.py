from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from astrynn_devforge.kernel import ApprovalDecision, CaseStatus, Sensitivity

from .auth import AuthRole


class APIModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class HealthResponse(APIModel):
    status: str = "ok"
    service: str = "astrynn-devforge"
    version: str = "0.4.0"
    persistence: str
    authentication: str = "bearer-rbac-development"


class PrincipalResponse(APIModel):
    actor_id: UUID
    organization_id: UUID
    role: AuthRole
    display_name: str


class CaseCreateRequest(APIModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)
    organization_id: UUID
    sensitivity: Sensitivity


class CaseTransitionRequest(APIModel):
    target: CaseStatus
    reason: str = Field(min_length=1, max_length=1000)


class ApprovalCreateRequest(APIModel):
    decision: ApprovalDecision
    rationale: str = Field(min_length=1, max_length=2000)
    conditions: tuple[str, ...] = ()


class CaseEventResponse(APIModel):
    event_type: str
    actor_id: UUID
    details: dict[str, object]
    created_at: datetime


class CaseResponse(APIModel):
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


class ApprovalResponse(APIModel):
    id: UUID
    case_id: UUID
    approver_id: UUID
    decision: ApprovalDecision
    rationale: str
    conditions: tuple[str, ...]
    created_at: datetime


class ErrorResponse(APIModel):
    detail: str

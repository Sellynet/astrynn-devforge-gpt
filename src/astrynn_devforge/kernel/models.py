from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from .enums import ApprovalDecision, ArtifactStatus, CaseStatus, Sensitivity


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class Organization:
    name: str
    id: UUID = field(default_factory=uuid4)
    country: str | None = None
    sector: str | None = None
    created_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class Actor:
    name: str
    role: str
    id: UUID = field(default_factory=uuid4)
    organization_id: UUID | None = None
    created_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class CaseEvent:
    event_type: str
    actor_id: UUID
    details: dict[str, Any]
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class Case:
    title: str
    owner_id: UUID
    organization_id: UUID
    sensitivity: Sensitivity
    id: UUID = field(default_factory=uuid4)
    description: str = ""
    status: CaseStatus = CaseStatus.DRAFT
    version: int = 1
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    events: list[CaseEvent] = field(default_factory=list)

    def record_event(self, event: CaseEvent) -> None:
        self.events.append(event)
        self.version += 1
        self.updated_at = utc_now()


@dataclass(frozen=True, slots=True)
class ApprovalRecord:
    case_id: UUID
    approver_id: UUID
    decision: ApprovalDecision
    rationale: str
    id: UUID = field(default_factory=uuid4)
    conditions: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class EvidenceReference:
    case_id: UUID
    label: str
    uri: str
    sensitivity: Sensitivity
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class OutputArtifact:
    case_id: UUID
    artifact_type: str
    owner_id: UUID
    content: dict[str, Any]
    id: UUID = field(default_factory=uuid4)
    version: int = 1
    status: ArtifactStatus = ArtifactStatus.DRAFT
    created_at: datetime = field(default_factory=utc_now)

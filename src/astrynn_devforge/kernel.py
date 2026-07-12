"""Kernel domain primitives for governed case lifecycle management."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import StrEnum


class CaseStatus(StrEnum):
    """Allowed lifecycle states for an Atlas, Aegis, or OAAA case."""

    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"


class DataSensitivity(StrEnum):
    """Minimal data classification used by the public-safe prototype."""

    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"


_ALLOWED_TRANSITIONS: dict[CaseStatus, frozenset[CaseStatus]] = {
    CaseStatus.DRAFT: frozenset({CaseStatus.IN_REVIEW, CaseStatus.CLOSED}),
    CaseStatus.IN_REVIEW: frozenset(
        {CaseStatus.DRAFT, CaseStatus.APPROVED, CaseStatus.REJECTED}
    ),
    CaseStatus.APPROVED: frozenset(
        {CaseStatus.ACTIVE, CaseStatus.SUSPENDED, CaseStatus.CLOSED}
    ),
    CaseStatus.REJECTED: frozenset({CaseStatus.DRAFT, CaseStatus.CLOSED}),
    CaseStatus.ACTIVE: frozenset({CaseStatus.SUSPENDED, CaseStatus.CLOSED}),
    CaseStatus.SUSPENDED: frozenset({CaseStatus.ACTIVE, CaseStatus.CLOSED}),
    CaseStatus.CLOSED: frozenset(),
}


@dataclass(frozen=True, slots=True)
class CaseEvent:
    """Immutable audit record for a lifecycle transition."""

    from_status: CaseStatus
    to_status: CaseStatus
    actor: str
    reason: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class Case:
    """A versioned unit of work governed by the Astrynn Kernel."""

    case_id: str
    title: str
    owner: str
    sensitivity: DataSensitivity = DataSensitivity.INTERNAL
    status: CaseStatus = CaseStatus.DRAFT
    version: int = 1
    history: tuple[CaseEvent, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError("case_id is required")
        if not self.title.strip():
            raise ValueError("title is required")
        if not self.owner.strip():
            raise ValueError("owner is required")
        if self.version < 1:
            raise ValueError("version must be at least 1")


def allowed_transitions(status: CaseStatus) -> frozenset[CaseStatus]:
    """Return the valid next states for a case status."""

    return _ALLOWED_TRANSITIONS[status]


def transition_case(
    case: Case,
    to_status: CaseStatus,
    *,
    actor: str,
    reason: str,
    occurred_at: datetime | None = None,
) -> Case:
    """Return a new case with an audited state transition.

    The original case is not mutated. This keeps the prototype's history explicit
    and prevents accidental loss of prior decisions.
    """

    if not actor.strip():
        raise ValueError("actor is required")
    if not reason.strip():
        raise ValueError("reason is required")
    if to_status not in allowed_transitions(case.status):
        raise ValueError(
            f"invalid transition: {case.status.value} -> {to_status.value}"
        )

    event = CaseEvent(
        from_status=case.status,
        to_status=to_status,
        actor=actor,
        reason=reason,
        occurred_at=occurred_at or datetime.now(UTC),
    )

    return replace(
        case,
        status=to_status,
        version=case.version + 1,
        history=(*case.history, event),
    )

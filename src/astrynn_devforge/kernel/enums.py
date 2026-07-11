from __future__ import annotations

from enum import StrEnum


class CaseStatus(StrEnum):
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"


class Sensitivity(StrEnum):
    GREEN = "GREEN"
    ORANGE = "ORANGE"
    RED = "RED"


class ApprovalDecision(StrEnum):
    APPROVE = "APPROVE"
    APPROVE_WITH_CONDITIONS = "APPROVE_WITH_CONDITIONS"
    REJECT = "REJECT"
    REQUIRE_SPECIALIST_REVIEW = "REQUIRE_SPECIALIST_REVIEW"


class ArtifactStatus(StrEnum):
    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"

from __future__ import annotations

from enum import StrEnum


class SourceKind(StrEnum):
    PUBLIC = "PUBLIC"
    MANUAL = "MANUAL"
    INTERNAL_APPROVED = "INTERNAL_APPROVED"
    SYNTHETIC = "SYNTHETIC"


class RiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ScenarioType(StrEnum):
    BASE = "BASE"
    ADVERSE = "ADVERSE"
    OPTIMISTIC = "OPTIMISTIC"
    STRESS = "STRESS"


class StatementType(StrEnum):
    FACT = "FACT"
    INFERENCE = "INFERENCE"
    ASSUMPTION = "ASSUMPTION"
    RECOMMENDATION = "RECOMMENDATION"

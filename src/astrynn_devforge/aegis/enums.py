from __future__ import annotations

from enum import StrEnum


class ClearanceDecision(StrEnum):
    APTO = "APTO"
    APTO_CON_CONTROLES = "APTO_CON_CONTROLES"
    NO_APTO_TODAVIA = "NO_APTO_TODAVIA"
    REQUIERE_REVISION_ESPECIALIZADA = "REQUIERE_REVISION_ESPECIALIZADA"


class RiskDimension(StrEnum):
    DATA = "data"
    PERMISSIONS = "permissions"
    AUTONOMY = "autonomy"
    IMPACT = "impact"
    TRACEABILITY = "traceability"
    HUMAN_OVERSIGHT = "human_oversight"
    EXTERNAL_DEPENDENCY = "external_dependency"
    ADVERSARIAL_ROBUSTNESS = "adversarial_robustness"
    INCIDENT_READINESS = "incident_readiness"


class SpecialistReviewTrigger(StrEnum):
    HEALTH = "health"
    EMPLOYMENT = "employment"
    CREDIT = "credit"
    MINORS = "minors"
    BIOMETRICS = "biometrics"
    LAW_ENFORCEMENT = "law_enforcement"
    SAFETY_CRITICAL = "safety_critical"
    CRITICAL_INFRASTRUCTURE = "critical_infrastructure"
    HIGHLY_SENSITIVE_DATA = "highly_sensitive_data"
    REGULATED_SECTOR = "regulated_sector"


class GuardrailPriority(StrEnum):
    ADVISORY = "ADVISORY"
    REQUIRED = "REQUIRED"
    BLOCKING = "BLOCKING"

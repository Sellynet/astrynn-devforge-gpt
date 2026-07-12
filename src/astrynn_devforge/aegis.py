"""Deterministic Aegis Deployment Clearance rules for the MVP."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ClearanceDecision(StrEnum):
    """Operational decisions emitted by Aegis."""

    APTO = "APTO"
    APTO_CON_CONTROLES = "APTO_CON_CONTROLES"
    NO_APTO_TODAVIA = "NO_APTO_TODAVIA"
    REVISION_ESPECIALIZADA = "REVISION_ESPECIALIZADA"


_SCORE_FIELDS = (
    "data",
    "permissions",
    "autonomy",
    "impact",
    "traceability",
    "human_oversight",
    "external_dependency",
    "adversarial_robustness",
    "incident_readiness",
)

_GUARDRAILS = {
    "data": "Reduce data exposure and document allowed and prohibited data.",
    "permissions": "Apply least privilege and explicit action-level permissions.",
    "autonomy": "Add human approval before high-impact actions.",
    "impact": "Limit blast radius, rate, scope, and financial exposure.",
    "traceability": "Enable complete logs, versions, sources, and decision history.",
    "human_oversight": "Name an accountable human owner and intervention path.",
    "external_dependency": "Document provider risk, fallback, and exit conditions.",
    "adversarial_robustness": "Run ARIA tests and remediate unresolved findings.",
    "incident_readiness": "Create disable, escalation, containment, and recovery steps.",
}


@dataclass(frozen=True, slots=True)
class ClearanceScorecard:
    """Nine Aegis risk dimensions, each scored from 0 to 5."""

    data: int
    permissions: int
    autonomy: int
    impact: int
    traceability: int
    human_oversight: int
    external_dependency: int
    adversarial_robustness: int
    incident_readiness: int

    def __post_init__(self) -> None:
        for field_name in _SCORE_FIELDS:
            value = getattr(self, field_name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{field_name} must be an integer")
            if not 0 <= value <= 5:
                raise ValueError(f"{field_name} must be between 0 and 5")

    @property
    def total(self) -> int:
        """Return the total Aegis risk score."""

        return sum(getattr(self, field_name) for field_name in _SCORE_FIELDS)

    def as_dict(self) -> dict[str, int]:
        """Return a stable machine-readable representation."""

        return {field_name: getattr(self, field_name) for field_name in _SCORE_FIELDS}


@dataclass(frozen=True, slots=True)
class ClearanceResult:
    """Explainable output of the deterministic clearance engine."""

    score: int
    decision: ClearanceDecision
    conditions: tuple[str, ...]
    rationale: str


_SPECIALIZED_DOMAINS = frozenset(
    {
        "health",
        "employment",
        "credit",
        "minors",
        "public_safety",
        "biometrics",
        "critical_infrastructure",
        "highly_sensitive_data",
        "regulated_sector",
    }
)


def requires_specialized_review(domains: set[str] | frozenset[str]) -> bool:
    """Return whether a case touches a domain requiring expert review."""

    normalized = {domain.strip().lower() for domain in domains if domain.strip()}
    return bool(normalized & _SPECIALIZED_DOMAINS)


def evaluate_clearance(
    scorecard: ClearanceScorecard,
    *,
    specialized_review: bool = False,
    unresolved_critical_findings: int = 0,
) -> ClearanceResult:
    """Evaluate an Aegis scorecard using conservative MVP rules.

    The 23-34 band is treated as NO_APTO_TODAVIA in v0.1. This removes
    ambiguity and forces redesign or re-evaluation before activation.
    """

    if unresolved_critical_findings < 0:
        raise ValueError("unresolved_critical_findings cannot be negative")

    conditions = tuple(
        _GUARDRAILS[field_name]
        for field_name in _SCORE_FIELDS
        if getattr(scorecard, field_name) >= 3
    )

    if specialized_review:
        return ClearanceResult(
            score=scorecard.total,
            decision=ClearanceDecision.REVISION_ESPECIALIZADA,
            conditions=conditions,
            rationale=(
                "The use case touches a regulated or highly sensitive domain and "
                "requires qualified legal, privacy, security, or sector review."
            ),
        )

    if unresolved_critical_findings > 0:
        return ClearanceResult(
            score=scorecard.total,
            decision=ClearanceDecision.NO_APTO_TODAVIA,
            conditions=conditions,
            rationale=(
                "Unresolved critical ARIA or security findings block controlled activation."
            ),
        )

    if scorecard.total <= 10:
        decision = ClearanceDecision.APTO
        rationale = "Low aggregate exposure with no specialized-review trigger."
    elif scorecard.total <= 22:
        decision = ClearanceDecision.APTO_CON_CONTROLES
        rationale = "Exposure is mitigable, but listed controls must be implemented first."
    else:
        decision = ClearanceDecision.NO_APTO_TODAVIA
        rationale = (
            "Aggregate exposure is too high for activation in the conservative MVP policy."
        )

    return ClearanceResult(
        score=scorecard.total,
        decision=decision,
        conditions=conditions,
        rationale=rationale,
    )

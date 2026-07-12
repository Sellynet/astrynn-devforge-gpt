import pytest

from astrynn_devforge.aegis import (
    ClearanceDecision,
    ClearanceScorecard,
    evaluate_clearance,
    requires_specialized_review,
)


def make_scorecard(**overrides: int) -> ClearanceScorecard:
    values = {
        "data": 0,
        "permissions": 0,
        "autonomy": 0,
        "impact": 0,
        "traceability": 0,
        "human_oversight": 0,
        "external_dependency": 0,
        "adversarial_robustness": 0,
        "incident_readiness": 0,
    }
    values.update(overrides)
    return ClearanceScorecard(**values)


def test_low_score_is_apto() -> None:
    result = evaluate_clearance(make_scorecard(data=2, permissions=2, impact=2))

    assert result.score == 6
    assert result.decision is ClearanceDecision.APTO


def test_middle_score_requires_controls() -> None:
    result = evaluate_clearance(
        make_scorecard(data=3, permissions=3, autonomy=3, impact=2)
    )

    assert result.score == 11
    assert result.decision is ClearanceDecision.APTO_CON_CONTROLES
    assert len(result.conditions) == 3


def test_score_of_23_is_no_apto_in_conservative_policy() -> None:
    result = evaluate_clearance(
        make_scorecard(
            data=3,
            permissions=3,
            autonomy=3,
            impact=3,
            traceability=3,
            human_oversight=2,
            external_dependency=2,
            adversarial_robustness=2,
            incident_readiness=2,
        )
    )

    assert result.score == 23
    assert result.decision is ClearanceDecision.NO_APTO_TODAVIA


def test_specialized_review_overrides_score() -> None:
    result = evaluate_clearance(make_scorecard(), specialized_review=True)

    assert result.score == 0
    assert result.decision is ClearanceDecision.REVISION_ESPECIALIZADA


def test_critical_aria_finding_blocks_activation() -> None:
    result = evaluate_clearance(
        make_scorecard(), unresolved_critical_findings=1
    )

    assert result.decision is ClearanceDecision.NO_APTO_TODAVIA


def test_specialized_domains_are_detected() -> None:
    assert requires_specialized_review({"Health", "marketing"}) is True
    assert requires_specialized_review({"marketing", "sales"}) is False


def test_score_dimension_outside_range_is_rejected() -> None:
    with pytest.raises(ValueError, match="between 0 and 5"):
        make_scorecard(data=6)


def test_boolean_is_not_accepted_as_integer_score() -> None:
    with pytest.raises(TypeError, match="must be an integer"):
        make_scorecard(data=True)

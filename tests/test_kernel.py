from datetime import UTC, datetime

import pytest

from astrynn_devforge.kernel import (
    Case,
    CaseStatus,
    DataSensitivity,
    allowed_transitions,
    transition_case,
)


def test_case_starts_as_draft() -> None:
    case = Case(case_id="CASE-001", title="Pilot", owner="Javier")

    assert case.status is CaseStatus.DRAFT
    assert case.version == 1
    assert case.history == ()
    assert case.sensitivity is DataSensitivity.INTERNAL


def test_valid_transition_returns_new_version_with_audit_event() -> None:
    case = Case(case_id="CASE-001", title="Pilot", owner="Javier")
    occurred_at = datetime(2026, 7, 11, 12, 0, tzinfo=UTC)

    reviewed = transition_case(
        case,
        CaseStatus.IN_REVIEW,
        actor="reviewer@astrynn",
        reason="Intake is complete",
        occurred_at=occurred_at,
    )

    assert case.status is CaseStatus.DRAFT
    assert reviewed.status is CaseStatus.IN_REVIEW
    assert reviewed.version == 2
    assert len(reviewed.history) == 1
    assert reviewed.history[0].actor == "reviewer@astrynn"
    assert reviewed.history[0].occurred_at == occurred_at


def test_invalid_transition_is_rejected() -> None:
    case = Case(case_id="CASE-001", title="Pilot", owner="Javier")

    with pytest.raises(ValueError, match="invalid transition"):
        transition_case(
            case,
            CaseStatus.ACTIVE,
            actor="reviewer@astrynn",
            reason="Trying to skip review",
        )


def test_closed_case_has_no_next_state() -> None:
    assert allowed_transitions(CaseStatus.CLOSED) == frozenset()


def test_required_identity_fields_are_validated() -> None:
    with pytest.raises(ValueError, match="case_id"):
        Case(case_id=" ", title="Pilot", owner="Javier")

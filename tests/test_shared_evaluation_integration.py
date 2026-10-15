"""Integration regression: actual OAAA service -> Aegis use-case -> shared evaluation envelope.

Uses the existing G-01 verified scenario builders, not synthetic stand-in handoffs.
"""
import pytest

from astrynn_devforge.oaaa import BlueprintStatus
from astrynn_devforge.shared.evaluation_adapter import (
    EvaluationBoundaryError,
    from_oaaa_aegis_handoff,
)
from test_oaaa_aegis_handoff import build_reviewed_blueprint, build_result

def test_real_oaaa_aegis_handoff_creates_evaluation_only_envelope():
    _service, repo, blueprint, _owner, _organization = build_reviewed_blueprint()
    _handoff_service, result = build_result(repo, blueprint)
    envelope = from_oaaa_aegis_handoff(
        result, expected_source_fingerprint=blueprint.safety_fingerprint
    )
    assert envelope.case_id == str(blueprint.case_id)
    assert envelope.organization_id == str(blueprint.organization_id)
    assert envelope.source_product == "KARVYNX"
    assert envelope.target_product == "QEVYNOR"
    assert envelope.status == "EVALUATION_ONLY"
    assert envelope.target_fingerprint == result.use_case.fingerprint()
    assert envelope.receipt()["handoff_fingerprint"] == result.handoff.fingerprint
    assert repo.latest_version(blueprint.blueprint_id).status == BlueprintStatus.IN_REVIEW

def test_real_handoff_rejects_stale_expectation():
    _service, repo, blueprint, _owner, _organization = build_reviewed_blueprint()
    _handoff_service, result = build_result(repo, blueprint)
    with pytest.raises(EvaluationBoundaryError):
        from_oaaa_aegis_handoff(result, expected_source_fingerprint="stale-source")

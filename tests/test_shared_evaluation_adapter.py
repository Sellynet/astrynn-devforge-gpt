"""BEL-AI-P0-001 synthetic boundary checks; existing OAAA handoff tests remain regression owner."""
from types import SimpleNamespace
from uuid import uuid4

import pytest

from astrynn_devforge.shared.evaluation_adapter import (
    EvaluationBoundaryError,
    from_oaaa_aegis_handoff,
)


class Target:
    def __init__(self, ids):
        self.id = uuid4()
        self.case_id, self.organization_id, self.owner_id = ids
    def fingerprint(self):
        return "target-fp"

class Handoff:
    schema_version = "OAAA-AEGIS-HANDOFF-0.1"
    source_safety_fingerprint = "source-fp"
    material_change = False
    blueprint_version = 1
    source_evidence_refs = ("vault://artifact/1",)
    supplemental_evidence_refs = ("case://context/1",)
    fingerprint = "handoff-fp"
    def __init__(self, target):
        self.case_id = target.case_id
        self.organization_id = target.organization_id
        self.owner_id = target.owner_id
        self.target_use_case_id = target.id
        self.target_fingerprint = target.fingerprint()

def fixture():
    target = Target((uuid4(), uuid4(), uuid4()))
    return SimpleNamespace(
        handoff=Handoff(target), use_case=target,
        acknowledgement=SimpleNamespace(state="ACCEPTED_FOR_EVALUATION"),
    )

def adapt(obj):
    return from_oaaa_aegis_handoff(obj, expected_source_fingerprint="source-fp")

def test_valid_evaluation_receipt():
    x = adapt(fixture())
    assert (x.source_product, x.target_product, x.status) == (
        "KARVYNX", "QEVYNOR", "EVALUATION_ONLY"
    )
    assert len(x.receipt()["sha256"]) == 64

def test_stale_source_rejected():
    with pytest.raises(EvaluationBoundaryError):
        from_oaaa_aegis_handoff(fixture(), expected_source_fingerprint="stale")

def test_tenant_mismatch_rejected():
    obj = fixture()
    obj.handoff.organization_id = uuid4()
    with pytest.raises(EvaluationBoundaryError):
        adapt(obj)

def test_target_tamper_rejected():
    obj = fixture()
    obj.handoff.target_fingerprint = "tampered"
    with pytest.raises(EvaluationBoundaryError):
        adapt(obj)

def test_ack_is_not_approval():
    obj = fixture()
    obj.acknowledgement.state = "APPROVED"
    with pytest.raises(EvaluationBoundaryError):
        adapt(obj)

def test_material_change_rejected():
    obj = fixture()
    obj.handoff.material_change = True
    with pytest.raises(EvaluationBoundaryError):
        adapt(obj)

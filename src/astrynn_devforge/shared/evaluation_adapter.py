"""Read-only shared evaluation adapter for the existing OAAA -> Aegis boundary.

Provides an evidence envelope, not an executor, IAM service or activation grant.
"""
import json
from dataclasses import dataclass
from hashlib import sha256

class EvaluationBoundaryError(ValueError):
    pass

@dataclass(frozen=True)
class EvaluationEnvelope:
    schema_version: str
    source_product: str
    target_product: str
    organization_id: str
    case_id: str
    owner_id: str
    blueprint_version: int
    source_fingerprint: str
    handoff_fingerprint: str
    target_fingerprint: str
    evidence_refs: tuple[str, ...]
    status: str = "EVALUATION_ONLY"

    def receipt(self):
        data = {key: list(value) if isinstance(value, tuple) else value
                for key, value in vars(self).items()}
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return {"status": self.status, "sha256": sha256(canonical.encode()).hexdigest(),
                "handoff_fingerprint": self.handoff_fingerprint}

def from_oaaa_aegis_handoff(result, *, expected_source_fingerprint: str) -> EvaluationEnvelope:
    """Consume a genuine OAAAtoAegisHandoffResult; no approval or execution."""
    handoff, target, ack = result.handoff, result.use_case, result.acknowledgement
    if getattr(ack.state, "value", ack.state) != "ACCEPTED_FOR_EVALUATION":
        raise EvaluationBoundaryError("Handoff not accepted for evaluation")
    if handoff.schema_version != "OAAA-AEGIS-HANDOFF-0.1":
        raise EvaluationBoundaryError("Unsupported source schema")
    if handoff.source_safety_fingerprint != expected_source_fingerprint:
        raise EvaluationBoundaryError("Stale source fingerprint")
    if handoff.material_change:
        raise EvaluationBoundaryError("Material source change requires a new evaluation")
    if (handoff.case_id != target.case_id or handoff.organization_id != target.organization_id
            or handoff.owner_id != target.owner_id or handoff.target_use_case_id != target.id):
        raise EvaluationBoundaryError("Identity mismatch")
    if handoff.target_fingerprint != target.fingerprint():
        raise EvaluationBoundaryError("Target integrity mismatch")
    refs = tuple(handoff.source_evidence_refs) + tuple(handoff.supplemental_evidence_refs)
    if not refs or any(not ref.strip() for ref in refs):
        raise EvaluationBoundaryError("Missing evidence")
    return EvaluationEnvelope(
        schema_version="ASTRYNN-EVALUATION-0.1", source_product="KARVYNX",
        target_product="QEVYNOR", organization_id=str(handoff.organization_id),
        case_id=str(handoff.case_id), owner_id=str(handoff.owner_id),
        blueprint_version=handoff.blueprint_version,
        source_fingerprint=handoff.source_safety_fingerprint,
        handoff_fingerprint=handoff.fingerprint,
        target_fingerprint=handoff.target_fingerprint, evidence_refs=refs,
    )

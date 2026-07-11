from __future__ import annotations

from typing import Any
from uuid import UUID

from astrynn_devforge.kernel import ArtifactStatus, EvidenceReference, OutputArtifact

from .enums import BlueprintStatus
from .service import BlueprintApprovalError
from .service import OAAAAgentBlueprintService as BaseOAAAAgentBlueprintService


class OAAAAgentBlueprintService(BaseOAAAAgentBlueprintService):
    """OAAA service with an ARIA gate on the public activation path."""

    def activate(
        self,
        *,
        blueprint_id: UUID,
        activated_by: UUID,
        activation_note: str,
        aria_receipt: Any | None = None,
    ):
        latest = self.blueprint_repository.latest_version(blueprint_id)
        if latest.status != BlueprintStatus.APPROVED:
            return super().activate(
                blueprint_id=blueprint_id,
                activated_by=activated_by,
                activation_note=activation_note,
            )
        if aria_receipt is None:
            raise BlueprintApprovalError("Activation requires a valid ARIA Receipt")

        receipt_blueprint_id = getattr(aria_receipt, "blueprint_id", None)
        receipt_fingerprint = getattr(aria_receipt, "blueprint_fingerprint", None)
        unresolved_critical = getattr(
            aria_receipt, "unresolved_critical_findings", None
        )
        verdict = getattr(aria_receipt, "verdict", None)
        verdict_value = getattr(verdict, "value", verdict)
        receipt_hash = getattr(aria_receipt, "receipt_hash", None)
        receipt_id = getattr(aria_receipt, "id", None)

        if receipt_blueprint_id != latest.blueprint_id:
            raise BlueprintApprovalError("ARIA Receipt belongs to another blueprint")
        if receipt_fingerprint != latest.safety_fingerprint:
            raise BlueprintApprovalError("ARIA Receipt belongs to a stale blueprint fingerprint")
        if unresolved_critical != 0:
            raise BlueprintApprovalError(
                "Open critical ARIA findings block activation"
            )
        if verdict_value not in {"PASS", "PASS_WITH_REMEDIATION"}:
            raise BlueprintApprovalError(
                f"ARIA verdict {verdict_value!r} does not permit activation"
            )
        if not isinstance(receipt_hash, str) or len(receipt_hash) != 64:
            raise BlueprintApprovalError("ARIA Receipt integrity hash is invalid")
        if receipt_id is None:
            raise BlueprintApprovalError("ARIA Receipt identifier is missing")

        active, activation_receipt = super().activate(
            blueprint_id=blueprint_id,
            activated_by=activated_by,
            activation_note=activation_note,
        )
        self.kernel_repository.append_evidence(
            EvidenceReference(
                case_id=active.case_id,
                label="OAAA activation linked to ARIA Receipt",
                uri=f"aria://receipts/{receipt_id}",
                sensitivity=active.sensitivity,
            )
        )
        self.kernel_repository.append_output(
            OutputArtifact(
                case_id=active.case_id,
                artifact_type="OAAA_ARIA_ACTIVATION_LINK",
                owner_id=active.owner_id,
                content={
                    "blueprint_id": str(active.blueprint_id),
                    "blueprint_version_id": str(active.id),
                    "blueprint_fingerprint": active.safety_fingerprint,
                    "aria_receipt_id": str(receipt_id),
                    "aria_receipt_hash": receipt_hash,
                    "aria_verdict": verdict_value,
                    "activation_receipt_id": str(activation_receipt.id),
                    "activation_receipt_hash": activation_receipt.receipt_hash,
                    "runtime_deployed": False,
                },
                version=active.version,
                status=ArtifactStatus.APPROVED,
            )
        )
        return active, activation_receipt

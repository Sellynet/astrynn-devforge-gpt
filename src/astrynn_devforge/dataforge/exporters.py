from __future__ import annotations

import json

from .models import VaultArtifactVersion, VaultProofReceipt


def export_json(
    artifact: VaultArtifactVersion,
    receipt: VaultProofReceipt | None = None,
) -> str:
    payload: dict[str, object] = {"artifact": artifact.to_dict()}
    if receipt is not None:
        payload["proof_receipt"] = receipt.to_dict()
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)


def export_markdown(
    artifact: VaultArtifactVersion,
    receipt: VaultProofReceipt | None = None,
) -> str:
    lines = [
        f"# {artifact.title}",
        "",
        f"- **Artifact ID:** `{artifact.artifact_id}`",
        f"- **Version:** {artifact.version}",
        f"- **Type:** `{artifact.artifact_type}`",
        f"- **Status:** `{artifact.status.value}`",
        f"- **Owner:** `{artifact.owner_id}`",
        f"- **Case:** `{artifact.case_id}`",
        f"- **Sensitivity:** `{artifact.sensitivity.value}`",
        f"- **Integrity hash:** `{artifact.integrity_hash}`",
        "",
        "## Content",
        "",
        "```json",
        json.dumps(artifact.content, indent=2, ensure_ascii=False, sort_keys=True),
        "```",
        "",
        "## Traceability",
        "",
        f"- Tests: {', '.join(artifact.test_references) or 'None recorded'}",
        f"- Evidence: {', '.join(artifact.evidence_references) or 'None recorded'}",
        f"- Conditions: {', '.join(artifact.conditions) or 'None'}",
        f"- Change summary: {artifact.change_summary or 'None'}",
    ]
    if receipt is not None:
        lines.extend(
            [
                "",
                "## Proof Receipt",
                "",
                f"- **Receipt ID:** `{receipt.id}`",
                f"- **Evaluator:** `{receipt.evaluator_id}`",
                f"- **Decision:** `{receipt.decision.value}`",
                f"- **Methodology:** `{receipt.methodology_version}`",
                f"- **Receipt hash:** `{receipt.receipt_hash}`",
                f"- **Created at:** `{receipt.created_at.isoformat()}`",
            ]
        )
    return "\n".join(lines) + "\n"

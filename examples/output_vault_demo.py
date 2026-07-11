from __future__ import annotations

import json
from uuid import uuid4

from astrynn_devforge.dataforge import (
    InMemoryOutputVaultRepository,
    OutputVaultService,
    VaultDecision,
    export_markdown,
)
from astrynn_devforge.kernel import InMemoryKernelRepository, KernelService, Sensitivity


def main() -> None:
    kernel_repository = InMemoryKernelRepository()
    kernel = KernelService(kernel_repository)
    owner_id = uuid4()
    evaluator_id = uuid4()
    organization_id = uuid4()
    case = kernel.create_case(
        title="Synthetic Aegis evidence case",
        description="Demonstration only",
        owner_id=owner_id,
        organization_id=organization_id,
        sensitivity=Sensitivity.ORANGE,
        actor_id=owner_id,
    )

    vault_repository = InMemoryOutputVaultRepository()
    vault = OutputVaultService(kernel_repository, vault_repository)
    draft = vault.create_draft(
        case_id=case.id,
        owner_id=owner_id,
        created_by=owner_id,
        artifact_type="AEGIS_CLEARANCE_REPORT",
        title="Synthetic deployment clearance",
        content={
            "decision": "APTO_CON_CONTROLES",
            "score": 18,
            "note": "Synthetic demonstration data only",
        },
        sensitivity=Sensitivity.ORANGE,
        test_references=("aria://synthetic-tests/001",),
        evidence_references=("evidence://synthetic/001",),
    )
    review = vault.submit_for_review(
        artifact_id=draft.artifact_id,
        submitted_by=owner_id,
    )
    package = vault.record_decision(
        artifact_id=draft.artifact_id,
        evaluator_id=evaluator_id,
        decision=VaultDecision.APPROVED_WITH_CONDITIONS,
        conditions=("Named human approval before every external action",),
        rationale="Synthetic controls and evidence verified",
    )

    result = {
        "versions": [
            item.to_dict()
            for item in vault_repository.versions_for_artifact(draft.artifact_id)
        ],
        "receipt": package.receipt.to_dict(),
        "kernel_case_status": kernel_repository.get_case(case.id).status.value,
        "kernel_output_count": len(kernel_repository.outputs_for_case(case.id)),
        "review_parent": str(review.parent_version_id),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(export_markdown(package.artifact, package.receipt))


if __name__ == "__main__":
    main()

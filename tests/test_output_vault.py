from uuid import uuid4

import pytest

from astrynn_devforge.dataforge import (
    InMemoryOutputVaultRepository,
    InvalidArtifactTransitionError,
    OutputVaultService,
    VaultApprovalError,
    VaultArtifactVersion,
    VaultDecision,
    export_json,
    export_markdown,
)
from astrynn_devforge.kernel import (
    ArtifactStatus,
    InMemoryKernelRepository,
    KernelService,
    Sensitivity,
)


def build_service(*, sensitivity: Sensitivity = Sensitivity.GREEN):
    kernel_repository = InMemoryKernelRepository()
    kernel = KernelService(kernel_repository)
    owner_id = uuid4()
    organization_id = uuid4()
    case = kernel.create_case(
        title="Output Vault test case",
        description="Controlled artifact lifecycle",
        owner_id=owner_id,
        organization_id=organization_id,
        sensitivity=sensitivity,
        actor_id=owner_id,
    )
    vault_repository = InMemoryOutputVaultRepository()
    vault = OutputVaultService(kernel_repository, vault_repository)
    return vault, vault_repository, kernel_repository, case, owner_id


def create_reviewable_draft(vault, case, owner_id):
    return vault.create_draft(
        case_id=case.id,
        owner_id=owner_id,
        created_by=owner_id,
        artifact_type="AEGIS_CLEARANCE_REPORT",
        title="Deployment clearance",
        content={"decision": "APTO_CON_CONTROLES", "score": 16},
        sensitivity=case.sensitivity,
        test_references=("aria://tests/001",),
        evidence_references=("evidence://case/001",),
    )


def test_append_only_lifecycle_creates_receipt_and_kernel_records() -> None:
    vault, repository, kernel_repository, case, owner_id = build_service()
    draft = create_reviewable_draft(vault, case, owner_id)
    review = vault.submit_for_review(
        artifact_id=draft.artifact_id,
        submitted_by=owner_id,
    )
    package = vault.record_decision(
        artifact_id=draft.artifact_id,
        evaluator_id=owner_id,
        decision=VaultDecision.APPROVED_WITH_CONDITIONS,
        conditions=("Human approval before external action",),
        rationale="Controls and evidence verified",
    )

    versions = repository.versions_for_artifact(draft.artifact_id)
    assert [item.version for item in versions] == [1, 2, 3]
    assert [item.status for item in versions] == [
        ArtifactStatus.DRAFT,
        ArtifactStatus.REVIEW,
        ArtifactStatus.APPROVED,
    ]
    assert draft.status == ArtifactStatus.DRAFT
    assert review.parent_version_id == draft.id
    assert package.artifact.parent_version_id == review.id
    assert package.receipt.artifact_integrity_hash == package.artifact.integrity_hash
    assert len(repository.receipts_for_artifact(draft.artifact_id)) == 1
    assert len(kernel_repository.outputs_for_case(case.id)) == 3
    assert len(kernel_repository.evidence_for_case(case.id)) == 4


def test_approval_requires_tests_and_evidence() -> None:
    vault, _, _, case, owner_id = build_service()
    draft = vault.create_draft(
        case_id=case.id,
        owner_id=owner_id,
        created_by=owner_id,
        artifact_type="ORBYN_ATLAS_BRIEFING",
        title="Briefing without evidence",
        content={"summary": "Draft"},
        sensitivity=Sensitivity.GREEN,
    )
    vault.submit_for_review(artifact_id=draft.artifact_id, submitted_by=owner_id)

    with pytest.raises(VaultApprovalError):
        vault.record_decision(
            artifact_id=draft.artifact_id,
            evaluator_id=owner_id,
            decision=VaultDecision.APPROVED,
            rationale="Attempted approval without evidence",
        )


def test_orange_artifact_requires_separate_evaluator() -> None:
    vault, _, _, case, owner_id = build_service(sensitivity=Sensitivity.ORANGE)
    draft = create_reviewable_draft(vault, case, owner_id)
    vault.submit_for_review(artifact_id=draft.artifact_id, submitted_by=owner_id)

    with pytest.raises(VaultApprovalError):
        vault.record_decision(
            artifact_id=draft.artifact_id,
            evaluator_id=owner_id,
            decision=VaultDecision.APPROVED,
            rationale="Owner cannot approve this sensitivity",
        )

    package = vault.record_decision(
        artifact_id=draft.artifact_id,
        evaluator_id=uuid4(),
        decision=VaultDecision.APPROVED,
        rationale="Independent evaluator approved",
    )
    assert package.artifact.status == ArtifactStatus.APPROVED


def test_integrity_hash_is_reproducible_for_same_substantive_payload() -> None:
    common = {
        "artifact_id": uuid4(),
        "case_id": uuid4(),
        "owner_id": uuid4(),
        "created_by": uuid4(),
        "artifact_type": "PROOF_RECEIPT",
        "title": "Stable payload",
        "content": {"b": 2, "a": 1},
        "sensitivity": Sensitivity.GREEN,
        "version": 1,
        "status": ArtifactStatus.REVIEW,
        "test_references": ("test://1",),
        "evidence_references": ("evidence://1",),
    }
    first = VaultArtifactVersion(**common)
    second = VaultArtifactVersion(**common)
    assert first.id != second.id
    assert first.integrity_hash == second.integrity_hash


def test_json_and_markdown_exports_include_traceability() -> None:
    vault, _, _, case, owner_id = build_service()
    draft = create_reviewable_draft(vault, case, owner_id)
    vault.submit_for_review(artifact_id=draft.artifact_id, submitted_by=owner_id)
    package = vault.record_decision(
        artifact_id=draft.artifact_id,
        evaluator_id=owner_id,
        decision=VaultDecision.APPROVED,
        rationale="Ready for controlled use",
    )

    json_export = export_json(package.artifact, package.receipt)
    markdown_export = export_markdown(package.artifact, package.receipt)
    assert package.artifact.integrity_hash in json_export
    assert package.receipt.receipt_hash in json_export
    assert "## Proof Receipt" in markdown_export
    assert "aria://tests/001" in markdown_export


def test_only_approved_artifacts_can_be_superseded() -> None:
    vault, repository, _, case, owner_id = build_service()
    draft = create_reviewable_draft(vault, case, owner_id)

    with pytest.raises(InvalidArtifactTransitionError):
        vault.supersede(
            artifact_id=draft.artifact_id,
            actor_id=owner_id,
            reason="Too early",
        )

    vault.submit_for_review(artifact_id=draft.artifact_id, submitted_by=owner_id)
    vault.record_decision(
        artifact_id=draft.artifact_id,
        evaluator_id=owner_id,
        decision=VaultDecision.APPROVED,
        rationale="Approved before replacement",
    )
    superseded = vault.supersede(
        artifact_id=draft.artifact_id,
        actor_id=owner_id,
        reason="Replaced by a newer governed artifact lineage",
    )
    assert superseded.status == ArtifactStatus.SUPERSEDED
    assert superseded.version == 4
    assert repository.latest_version(draft.artifact_id).id == superseded.id

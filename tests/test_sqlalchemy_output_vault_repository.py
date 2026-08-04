from pathlib import Path
from uuid import uuid4

from astrynn_devforge.dataforge import (
    VaultArtifactVersion,
    VaultDecision,
    VaultProofReceipt,
)
from astrynn_devforge.kernel import ArtifactStatus, Sensitivity
from astrynn_devforge.persistence import SQLAlchemyOutputVaultRepository


def test_sqlalchemy_output_vault_survives_restart(
    tmp_path: Path,
) -> None:
    database_url = (
        f"sqlite:///{(tmp_path / 'output-vault.db').as_posix()}"
    )
    artifact = VaultArtifactVersion(
        artifact_id=uuid4(),
        case_id=uuid4(),
        owner_id=uuid4(),
        created_by=uuid4(),
        artifact_type="OAAA_AGENT_BLUEPRINT",
        title="Persistent governed blueprint",
        content={
            "blueprint_id": str(uuid4()),
            "status": "DRAFT",
        },
        sensitivity=Sensitivity.GREEN,
        version=1,
        status=ArtifactStatus.DRAFT,
        test_references=("test://oaaa/restart",),
        evidence_references=("evidence://oaaa/restart",),
        change_summary="Initial persistent draft",
    )

    first = SQLAlchemyOutputVaultRepository(
        database_url,
        create_schema=True,
    )
    stored = first.append_version(artifact)
    first.close()

    second = SQLAlchemyOutputVaultRepository(
        database_url,
        create_schema=False,
    )
    recovered = second.latest_version(artifact.artifact_id)
    history = second.versions_for_artifact(
        artifact.artifact_id
    )
    second.close()

    assert recovered.to_dict() == stored.to_dict()
    assert history == (stored,)



def test_sqlalchemy_output_vault_receipt_survives_restart(
    tmp_path: Path,
) -> None:
    database_url = (
        f"sqlite:///{(tmp_path / 'output-vault-receipt.db').as_posix()}"
    )
    artifact = VaultArtifactVersion(
        artifact_id=uuid4(),
        case_id=uuid4(),
        owner_id=uuid4(),
        created_by=uuid4(),
        artifact_type="AEGIS_CLEARANCE_REPORT",
        title="Persistent clearance evidence",
        content={"decision": "APTO_CON_CONTROLES"},
        sensitivity=Sensitivity.GREEN,
        version=1,
        status=ArtifactStatus.APPROVED,
        decision=VaultDecision.APPROVED,
        test_references=("aria://tests/restart",),
        evidence_references=("evidence://restart",),
        change_summary="Approved persistent artifact",
    )
    receipt = VaultProofReceipt(
        artifact_id=artifact.artifact_id,
        artifact_version_id=artifact.id,
        case_id=artifact.case_id,
        version=artifact.version,
        evaluator_id=uuid4(),
        decision=VaultDecision.APPROVED,
        conditions=(),
        test_references=artifact.test_references,
        evidence_references=artifact.evidence_references,
        artifact_integrity_hash=artifact.integrity_hash,
    )

    first = SQLAlchemyOutputVaultRepository(
        database_url,
        create_schema=True,
    )
    first.append_version(artifact)
    stored_receipt = first.append_receipt(receipt)
    first.close()

    second = SQLAlchemyOutputVaultRepository(
        database_url,
        create_schema=False,
    )
    recovered = second.receipts_for_artifact(
        artifact.artifact_id
    )
    second.close()

    assert len(recovered) == 1
    assert recovered[0].to_dict() == stored_receipt.to_dict()

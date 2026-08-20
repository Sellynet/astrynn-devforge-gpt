from __future__ import annotations

import os
from dataclasses import replace
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from test_api_persistence import _persistent_oaaa_payload
from test_sqlalchemy_oaaa_repository import build_blueprint

from astrynn_devforge.aegis import ClearanceDecision
from astrynn_devforge.api import create_app
from astrynn_devforge.api.auth import AuthRole, Principal
from astrynn_devforge.api.container import build_container
from astrynn_devforge.dataforge import (
    DuplicateArtifactVersionError,
    VaultApprovalError,
    VaultArtifactVersion,
    VaultDecision,
    VaultProofReceipt,
)
from astrynn_devforge.kernel import ArtifactStatus, Sensitivity
from astrynn_devforge.oaaa import (
    ActivationReceipt,
    DuplicateBlueprintVersionError,
    HumanApprovalRecord,
    HumanDecision,
)

POSTGRES_URL_ENV = "ASTRYNN_POSTGRES_TEST_URL"


def _postgres_url() -> str:
    database_url = os.getenv(POSTGRES_URL_ENV, "").strip()
    if not database_url:
        pytest.skip(
            f"{POSTGRES_URL_ENV} is not configured"
        )
    return database_url


def _close_container(container) -> None:
    for name in (
        "kernel_repository",
        "blueprint_repository",
        "output_vault_repository",
    ):
        repository = getattr(container, name)
        close = getattr(repository, "close", None)
        if close is not None:
            close()


def test_postgresql_oaaa_workflow_survives_restart() -> None:
    database_url = _postgres_url()

    organization_id = uuid4()
    owner = Principal(
        actor_id=uuid4(),
        organization_id=organization_id,
        role=AuthRole.CASE_OWNER,
        display_name="PostgreSQL persistence owner",
    )

    tokens = {"postgres-persistence-token": owner}
    headers = {
        "Authorization": "Bearer postgres-persistence-token",
    }

    first_container = build_container(
        tokens,
        database_url=database_url,
        create_schema=True,
    )

    try:
        with TestClient(
            create_app(first_container),
            raise_server_exceptions=True,
        ) as first:
            system_status = first.get("/status")

            assert system_status.status_code == 200
            assert (
                system_status.json()["persistence"]
                == "sqlalchemy-postgresql"
            )
            assert (
                system_status.json()["oaaa_control_plane_persistence"]
                == "sqlalchemy-postgresql"
            )
            assert (
                first_container.output_vault_repository.persistence_name
                == "sqlalchemy-postgresql"
            )

            created_case = first.post(
                "/api/v1/cases",
                headers=headers,
                json={
                    "title": "PostgreSQL persistent OAAA case",
                    "description": "Synthetic PostgreSQL restart test",
                    "organization_id": str(organization_id),
                    "sensitivity": "GREEN",
                },
            )
            assert created_case.status_code == 201
            case_id = created_case.json()["id"]

            created_blueprint = first.post(
                f"/api/v1/oaaa/cases/{case_id}/blueprints",
                headers=headers,
                json=_persistent_oaaa_payload(),
            )
            assert created_blueprint.status_code == 201

            original = created_blueprint.json()["blueprint"]
            blueprint_id = original["blueprint_id"]

    finally:
        _close_container(first_container)

    second_container = build_container(
        tokens,
        database_url=database_url,
        create_schema=False,
    )

    try:
        with TestClient(
            create_app(second_container),
            raise_server_exceptions=True,
        ) as second:
            recovered = second.get(
                f"/api/v1/oaaa/blueprints/{blueprint_id}",
                headers=headers,
            )
            assert recovered.status_code == 200

            recovered_blueprint = recovered.json()["blueprint"]

            assert recovered_blueprint["id"] == original["id"]
            assert (
                recovered_blueprint["safety_fingerprint"]
                == original["safety_fingerprint"]
            )
            assert (
                recovered_blueprint["owner_id"]
                == original["owner_id"]
            )

            revision_payload = _persistent_oaaa_payload()
            revision_payload["objective"] = (
                "Summarize approved evidence and compare bounded scenarios"
            )
            revision_payload["change_summary"] = (
                "Add bounded comparison after PostgreSQL restart"
            )

            revised = second.post(
                (
                    f"/api/v1/oaaa/blueprints/"
                    f"{blueprint_id}/revisions"
                ),
                headers=headers,
                json=revision_payload,
            )

            assert revised.status_code == 201
            assert revised.json()["blueprint"]["version"] == 2
            assert (
                revised.json()["blueprint"]["parent_version_id"]
                == original["id"]
            )

            submitted = second.post(
                f"/api/v1/oaaa/blueprints/{blueprint_id}/submit",
                headers=headers,
                json={
                    "reason": (
                        "Recovered PostgreSQL blueprint ready for review"
                    )
                },
            )

            assert submitted.status_code == 200
            assert (
                submitted.json()["blueprint"]["status"]
                == "IN_REVIEW"
            )
            assert submitted.json()["blueprint"]["version"] == 3

    finally:
        _close_container(second_container)



def test_postgresql_repository_contracts_survive_restart() -> None:
    database_url = _postgres_url()

    first_container = build_container(
        {},
        database_url=database_url,
        create_schema=True,
    )

    try:
        blueprint_repository = first_container.blueprint_repository
        vault_repository = first_container.output_vault_repository

        original = blueprint_repository.append_version(build_blueprint())

        with pytest.raises(DuplicateBlueprintVersionError):
            blueprint_repository.append_version(original)

        skipped = replace(
            original,
            id=uuid4(),
            version=3,
            parent_version_id=original.id,
        )
        with pytest.raises(DuplicateBlueprintVersionError):
            blueprint_repository.append_version(skipped)

        wrong_parent = replace(
            original,
            id=uuid4(),
            version=2,
            parent_version_id=uuid4(),
        )
        with pytest.raises(DuplicateBlueprintVersionError):
            blueprint_repository.append_version(wrong_parent)

        assert blueprint_repository.versions_for_blueprint(
            original.blueprint_id
        ) == (original,)

        second_version = replace(
            original,
            id=uuid4(),
            version=2,
            parent_version_id=original.id,
        )
        stored_second = blueprint_repository.append_version(second_version)

        approval = HumanApprovalRecord(
            blueprint_id=stored_second.blueprint_id,
            blueprint_version_id=stored_second.id,
            blueprint_fingerprint=stored_second.safety_fingerprint,
            approver_id=uuid4(),
            decision=HumanDecision.APPROVE,
            rationale="Synthetic PostgreSQL approval persistence gate",
            clearance_result_id=uuid4(),
            vault_receipt_id=uuid4(),
            vault_receipt_hash="a" * 64,
        )
        stored_approval = blueprint_repository.append_approval(approval)

        activation = ActivationReceipt(
            blueprint_id=stored_second.blueprint_id,
            blueprint_version_id=stored_second.id,
            blueprint_fingerprint=stored_second.safety_fingerprint,
            clearance_result_id=uuid4(),
            clearance_decision=ClearanceDecision.APTO,
            human_approval_id=stored_approval.id,
            activated_by=uuid4(),
            activation_note=(
                "Synthetic governance activation for PostgreSQL persistence"
            ),
            vault_receipt_id=uuid4(),
            vault_receipt_hash="b" * 64,
        )
        stored_activation = (
            blueprint_repository.append_activation_receipt(activation)
        )

        artifact = VaultArtifactVersion(
            artifact_id=uuid4(),
            case_id=stored_second.case_id,
            owner_id=stored_second.owner_id,
            created_by=stored_second.created_by,
            artifact_type="AEGIS_CLEARANCE_REPORT",
            title="PostgreSQL persistent clearance evidence",
            content={"decision": "APTO"},
            sensitivity=Sensitivity.GREEN,
            version=1,
            status=ArtifactStatus.APPROVED,
            decision=VaultDecision.APPROVED,
            test_references=("test://postgresql/contract",),
            evidence_references=("evidence://postgresql/contract",),
            change_summary="Initial PostgreSQL contract artifact",
        )
        stored_artifact = vault_repository.append_version(artifact)

        with pytest.raises(DuplicateArtifactVersionError):
            vault_repository.append_version(artifact)

        receipt = VaultProofReceipt(
            artifact_id=stored_artifact.artifact_id,
            artifact_version_id=stored_artifact.id,
            case_id=stored_artifact.case_id,
            version=stored_artifact.version,
            evaluator_id=uuid4(),
            decision=VaultDecision.APPROVED,
            conditions=(),
            test_references=stored_artifact.test_references,
            evidence_references=stored_artifact.evidence_references,
            artifact_integrity_hash=stored_artifact.integrity_hash,
        )
        stored_receipt = vault_repository.append_receipt(receipt)

    finally:
        _close_container(first_container)

    second_container = build_container(
        {},
        database_url=database_url,
        create_schema=False,
    )

    try:
        history = second_container.blueprint_repository.versions_for_blueprint(
            original.blueprint_id
        )
        approvals = (
            second_container.blueprint_repository.approvals_for_blueprint(
                original.blueprint_id
            )
        )
        activations = (
            second_container.blueprint_repository
            .activation_receipts_for_blueprint(original.blueprint_id)
        )
        recovered_artifact = (
            second_container.output_vault_repository.latest_version(
                stored_artifact.artifact_id
            )
        )
        recovered_receipts = (
            second_container.output_vault_repository.receipts_for_artifact(
                stored_artifact.artifact_id
            )
        )

        assert [item.version for item in history] == [1, 2]
        assert history[1].parent_version_id == history[0].id
        assert approvals == (stored_approval,)
        assert activations == (stored_activation,)
        assert recovered_artifact.to_dict() == stored_artifact.to_dict()
        assert recovered_receipts == (stored_receipt,)

    finally:
        _close_container(second_container)


def test_postgresql_cross_org_isolation_and_atomic_vault_rejection() -> None:
    database_url = _postgres_url()

    organization_a = uuid4()
    organization_b = uuid4()

    owner_a = Principal(
        actor_id=uuid4(),
        organization_id=organization_a,
        role=AuthRole.CASE_OWNER,
        display_name="PostgreSQL Owner A",
    )
    owner_b = Principal(
        actor_id=uuid4(),
        organization_id=organization_b,
        role=AuthRole.CASE_OWNER,
        display_name="PostgreSQL Owner B",
    )

    tokens = {
        "postgres-owner-a": owner_a,
        "postgres-owner-b": owner_b,
    }
    headers_a = {
        "Authorization": "Bearer postgres-owner-a",
    }
    headers_b = {
        "Authorization": "Bearer postgres-owner-b",
    }

    container = build_container(
        tokens,
        database_url=database_url,
        create_schema=True,
    )

    try:
        with TestClient(
            create_app(container),
            raise_server_exceptions=True,
        ) as api:
            created_case = api.post(
                "/api/v1/cases",
                headers=headers_a,
                json={
                    "title": "PostgreSQL organization isolation case",
                    "description": "Synthetic cross-organization gate",
                    "organization_id": str(organization_a),
                    "sensitivity": "GREEN",
                },
            )
            assert created_case.status_code == 201
            case_id = UUID(created_case.json()["id"])

            created_blueprint = api.post(
                f"/api/v1/oaaa/cases/{case_id}/blueprints",
                headers=headers_a,
                json=_persistent_oaaa_payload(),
            )
            assert created_blueprint.status_code == 201
            blueprint_id = created_blueprint.json()["blueprint"][
                "blueprint_id"
            ]

            cross_org_read = api.get(
                f"/api/v1/oaaa/blueprints/{blueprint_id}",
                headers=headers_b,
            )
            assert cross_org_read.status_code == 403

            before_artifacts = (
                container.output_vault_repository.list_latest()
            )
            before_outputs = (
                container.kernel_repository.outputs_for_case(case_id)
            )
            before_evidence = (
                container.kernel_repository.evidence_for_case(case_id)
            )

            with pytest.raises(VaultApprovalError, match="owner_id"):
                container.output_vault_service.create_draft(
                    case_id=case_id,
                    owner_id=owner_b.actor_id,
                    created_by=owner_b.actor_id,
                    artifact_type="AEGIS_CLEARANCE_REPORT",
                    title="Unauthorized PostgreSQL artifact",
                    content={"decision": "APTO"},
                    sensitivity=Sensitivity.GREEN,
                    test_references=("test://postgresql/atomicity",),
                    evidence_references=(
                        "evidence://postgresql/atomicity",
                    ),
                )

            assert (
                container.output_vault_repository.list_latest()
                == before_artifacts
            )
            assert (
                container.kernel_repository.outputs_for_case(case_id)
                == before_outputs
            )
            assert (
                container.kernel_repository.evidence_for_case(case_id)
                == before_evidence
            )

    finally:
        _close_container(container)

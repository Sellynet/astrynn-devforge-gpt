from __future__ import annotations

import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from test_api_persistence import _persistent_oaaa_payload

from astrynn_devforge.api import create_app
from astrynn_devforge.api.auth import AuthRole, Principal
from astrynn_devforge.api.container import build_container

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
            health = first.get("/health")

            assert health.status_code == 200
            assert (
                health.json()["persistence"]
                == "sqlalchemy-postgresql"
            )
            assert (
                health.json()["oaaa_control_plane_persistence"]
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

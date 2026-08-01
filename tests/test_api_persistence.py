from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from astrynn_devforge.api import create_app
from astrynn_devforge.api.auth import AuthRole, Principal
from astrynn_devforge.api.container import build_container
from astrynn_devforge.persistence import (
    SQLAlchemyAgentBlueprintRepository,
    SQLAlchemyOutputVaultRepository,
)


def test_api_recovers_case_from_shared_sqlite_database(tmp_path: Path) -> None:
    organization_id = uuid4()
    principal = Principal(
        actor_id=uuid4(),
        organization_id=organization_id,
        role=AuthRole.CASE_OWNER,
        display_name="Persistent owner",
    )
    tokens = {"persistent-token": principal}
    database_url = f"sqlite:///{(tmp_path / 'api.db').as_posix()}"
    headers = {"Authorization": "Bearer persistent-token"}

    first = TestClient(
        create_app(
            build_container(
                tokens,
                database_url=database_url,
                create_schema=True,
            )
        )
    )
    created = first.post(
        "/api/v1/cases",
        headers=headers,
        json={
            "title": "Persistent API case",
            "description": "Synthetic restart test",
            "organization_id": str(organization_id),
            "sensitivity": "GREEN",
        },
    )
    assert created.status_code == 201
    case_id = created.json()["id"]

    second = TestClient(
        create_app(
            build_container(
                tokens,
                database_url=database_url,
                create_schema=False,
            )
        )
    )
    recovered = second.get(f"/api/v1/cases/{case_id}", headers=headers)
    health = second.get("/health")

    assert recovered.status_code == 200
    assert recovered.json()["title"] == "Persistent API case"
    assert health.json()["persistence"] == "sqlalchemy-sqlite"



def test_container_uses_sqlite_for_oaaa_control_plane(
    tmp_path: Path,
) -> None:
    database_url = (
        f"sqlite:///{(tmp_path / 'container-oaaa.db').as_posix()}"
    )

    container = build_container(
        {},
        database_url=database_url,
        create_schema=True,
    )
    api = TestClient(create_app(container))
    health = api.get("/health")

    assert isinstance(
        container.blueprint_repository,
        SQLAlchemyAgentBlueprintRepository,
    )
    assert (
        container.oaaa_control_plane_persistence
        == "sqlalchemy-sqlite"
    )
    assert health.status_code == 200
    assert (
        health.json()["oaaa_control_plane_persistence"]
        == "sqlalchemy-sqlite"
    )



def _persistent_oaaa_payload() -> dict[str, object]:
    return {
        "name": "Persistent governed briefing agent",
        "business_need": (
            "Preserve a governed agent blueprint across application restarts"
        ),
        "role": (
            "Prepare evidence-linked briefings under human review"
        ),
        "objective": (
            "Summarize approved evidence without autonomous external action"
        ),
        "tools": [
            {
                "name": "approved-case-records",
                "allowed_operations": [
                    "read approved case context",
                ],
                "prohibited_operations": [
                    "write case state",
                    "delete evidence",
                ],
                "requires_human_approval": False,
            }
        ],
        "data_boundary": {
            "allowed_categories": [
                "approved case evidence",
                "synthetic test data",
            ],
            "prohibited_categories": [
                "credentials",
                "unapproved personal data",
            ],
            "retention_rule": (
                "Retain references only while the case remains open"
            ),
            "deletion_rule": (
                "Remove working copies when the case is closed"
            ),
        },
        "allowed_actions": [
            "summarize approved case evidence",
            "draft a human-reviewable recommendation",
        ],
        "prohibited_actions": [
            "send external messages",
            "execute tools without approval",
            "modify case evidence",
        ],
        "autonomy_level": "ADVISORY",
        "approval_points": [
            {
                "trigger": (
                    "before any external or mutating action"
                ),
                "approver_role": "REVIEWER",
                "action_if_unavailable": "STOP",
            }
        ],
        "logs_required": [
            "input evidence references",
            "decision rationale",
            "human approval records",
        ],
        "aria_test_plan": [
            {
                "family": "PROMPT_INJECTION",
                "objective": (
                    "Reject instructions that conflict "
                    "with the governed role"
                ),
                "pass_criteria": (
                    "No prohibited action or data access is accepted"
                ),
            },
            {
                "family": "TOOL_PERMISSION_DRIFT",
                "objective": (
                    "Keep tool use inside the declared operation set"
                ),
                "pass_criteria": (
                    "Every undeclared operation is refused and logged"
                ),
            },
            {
                "family": "INCIDENT_TRIGGER",
                "objective": (
                    "Stop safely when an incident threshold is reached"
                ),
                "pass_criteria": (
                    "The agent stops and requests named human review"
                ),
            },
        ],
        "rollback_procedure": (
            "Return to the previous approved blueprint version"
        ),
        "disable_procedure": (
            "Disable all tool grants and preserve the audit trail"
        ),
    }


def test_oaaa_http_workflow_continues_after_sqlite_restart(
    tmp_path: Path,
) -> None:
    organization_id = uuid4()
    owner = Principal(
        actor_id=uuid4(),
        organization_id=organization_id,
        role=AuthRole.CASE_OWNER,
        display_name="Persistent OAAA owner",
    )
    tokens = {"persistent-oaaa-token": owner}
    headers = {
        "Authorization": "Bearer persistent-oaaa-token",
    }
    database_url = (
        f"sqlite:///{(tmp_path / 'oaaa-http-restart.db').as_posix()}"
    )

    first_container = build_container(
        tokens,
        database_url=database_url,
        create_schema=True,
    )
    first = TestClient(create_app(first_container))

    created_case = first.post(
        "/api/v1/cases",
        headers=headers,
        json={
            "title": "Persistent OAAA case",
            "description": "Synthetic full restart test",
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

    second_container = build_container(
        tokens,
        database_url=database_url,
        create_schema=False,
    )
    second = TestClient(
        create_app(second_container),
        raise_server_exceptions=True,
    )

    recovered = second.get(
        f"/api/v1/oaaa/blueprints/{blueprint_id}",
        headers=headers,
    )

    revision_payload = _persistent_oaaa_payload()
    revision_payload["objective"] = (
        "Summarize approved evidence and compare bounded scenarios"
    )
    revision_payload["change_summary"] = (
        "Add bounded scenario comparison after restart"
    )

    revised = second.post(
        f"/api/v1/oaaa/blueprints/{blueprint_id}/revisions",
        headers=headers,
        json=revision_payload,
    )

    submitted = second.post(
        f"/api/v1/oaaa/blueprints/{blueprint_id}/submit",
        headers=headers,
        json={
            "reason": (
                "Recovered blueprint ready for independent review"
            )
        },
    )

    assert recovered.status_code == 200
    assert recovered.json()["blueprint"]["id"] == original["id"]
    assert (
        recovered.json()["blueprint"]["safety_fingerprint"]
        == original["safety_fingerprint"]
    )

    assert revised.status_code == 201
    assert revised.json()["blueprint"]["version"] == 2
    assert (
        revised.json()["blueprint"]["parent_version_id"]
        == original["id"]
    )

    assert submitted.status_code == 200
    assert submitted.json()["blueprint"]["status"] == "IN_REVIEW"
    assert submitted.json()["blueprint"]["version"] == 3



def test_container_uses_sqlite_for_output_vault(
    tmp_path: Path,
) -> None:
    database_url = (
        f"sqlite:///{(tmp_path / 'container-vault.db').as_posix()}"
    )

    container = build_container(
        {},
        database_url=database_url,
        create_schema=True,
    )

    assert isinstance(
        container.output_vault_repository,
        SQLAlchemyOutputVaultRepository,
    )

from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from astrynn_devforge.api import create_app
from astrynn_devforge.api.auth import AuthRole, Principal
from astrynn_devforge.api.container import build_container


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

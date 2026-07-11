from uuid import uuid4

from fastapi.testclient import TestClient

from astrynn_devforge.api import create_app
from astrynn_devforge.api.container import build_container


def client() -> TestClient:
    return TestClient(create_app(build_container()))


def case_payload(*, sensitivity: str = "GREEN") -> dict[str, str]:
    owner_id = str(uuid4())
    return {
        "title": "Controlled AI deployment",
        "description": "Synthetic API test case",
        "owner_id": owner_id,
        "organization_id": str(uuid4()),
        "sensitivity": sensitivity,
        "actor_id": owner_id,
    }


def test_health() -> None:
    response = client().get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["persistence"] == "in-memory-development"


def test_create_list_and_get_case() -> None:
    api = client()
    created = api.post("/api/v1/cases", json=case_payload())
    assert created.status_code == 201
    case_id = created.json()["id"]
    assert created.json()["status"] == "DRAFT"

    listed = api.get("/api/v1/cases")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    fetched = api.get(f"/api/v1/cases/{case_id}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == case_id


def test_transition_requires_valid_kernel_state() -> None:
    api = client()
    created = api.post("/api/v1/cases", json=case_payload()).json()

    invalid = api.post(
        f"/api/v1/cases/{created['id']}/transition",
        json={
            "target": "ACTIVE",
            "actor_id": created["owner_id"],
            "reason": "Skip governance",
        },
    )
    assert invalid.status_code == 409


def test_approval_and_controlled_transition() -> None:
    api = client()
    created = api.post("/api/v1/cases", json=case_payload()).json()
    case_id = created["id"]
    owner_id = created["owner_id"]

    review = api.post(
        f"/api/v1/cases/{case_id}/transition",
        json={"target": "IN_REVIEW", "actor_id": owner_id, "reason": "Ready for review"},
    )
    assert review.status_code == 200

    approval = api.post(
        f"/api/v1/cases/{case_id}/approvals",
        json={
            "approver_id": owner_id,
            "decision": "APPROVE_WITH_CONDITIONS",
            "rationale": "Synthetic case with bounded scope",
            "conditions": ["Human approval before external action"],
        },
    )
    assert approval.status_code == 201

    approved = api.post(
        f"/api/v1/cases/{case_id}/transition",
        json={"target": "APPROVED", "actor_id": owner_id, "reason": "Approval recorded"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "APPROVED"


def test_orange_case_rejects_owner_self_approval() -> None:
    api = client()
    created = api.post("/api/v1/cases", json=case_payload(sensitivity="ORANGE")).json()

    response = api.post(
        f"/api/v1/cases/{created['id']}/approvals",
        json={
            "approver_id": created["owner_id"],
            "decision": "APPROVE",
            "rationale": "Owner should not approve this case",
            "conditions": [],
        },
    )
    assert response.status_code == 403


def test_missing_case_returns_404() -> None:
    response = client().get(f"/api/v1/cases/{uuid4()}")
    assert response.status_code == 404

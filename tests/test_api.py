from uuid import uuid4

from fastapi.testclient import TestClient

from astrynn_devforge.api import create_app
from astrynn_devforge.api.auth import AuthRole, Principal
from astrynn_devforge.api.container import build_container

ORG_A = uuid4()
ORG_B = uuid4()
OWNER_A = Principal(uuid4(), ORG_A, AuthRole.CASE_OWNER, "Owner A")
OWNER_A_2 = Principal(uuid4(), ORG_A, AuthRole.CASE_OWNER, "Owner A2")
REVIEWER_A = Principal(uuid4(), ORG_A, AuthRole.REVIEWER, "Reviewer A")
VIEWER_A = Principal(uuid4(), ORG_A, AuthRole.VIEWER, "Viewer A")
OWNER_B = Principal(uuid4(), ORG_B, AuthRole.CASE_OWNER, "Owner B")
SYSTEM_ADMIN = Principal(uuid4(), ORG_A, AuthRole.SYSTEM_ADMIN, "System Admin")

TOKENS = {
    "owner-a-token": OWNER_A,
    "owner-a2-token": OWNER_A_2,
    "reviewer-a-token": REVIEWER_A,
    "viewer-a-token": VIEWER_A,
    "owner-b-token": OWNER_B,
    "system-admin-token": SYSTEM_ADMIN,
}


def client() -> TestClient:
    return TestClient(create_app(build_container(TOKENS)))


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def case_payload(*, organization_id=ORG_A, sensitivity: str = "GREEN") -> dict[str, str]:
    return {
        "title": "Controlled AI deployment",
        "description": "Synthetic API test case",
        "organization_id": str(organization_id),
        "sensitivity": sensitivity,
    }


def create_case(api: TestClient, token: str = "owner-a-token", **kwargs):
    return api.post(
        "/api/v1/cases",
        json=case_payload(**kwargs),
        headers=auth(token),
    )


def test_health_is_public_but_reports_authentication_mode() -> None:
    response = client().get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["authentication"] == "bearer-rbac-development"


def test_protected_endpoint_requires_bearer_token() -> None:
    response = client().get("/api/v1/cases")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_invalid_token_is_rejected() -> None:
    response = client().get("/api/v1/cases", headers=auth("wrong-token"))

    assert response.status_code == 401


def test_me_returns_authenticated_principal() -> None:
    response = client().get("/api/v1/me", headers=auth("reviewer-a-token"))

    assert response.status_code == 200
    assert response.json()["actor_id"] == str(REVIEWER_A.actor_id)
    assert response.json()["organization_id"] == str(ORG_A)
    assert response.json()["role"] == "REVIEWER"


def test_owner_creates_case_as_authenticated_actor() -> None:
    response = create_case(client())

    assert response.status_code == 201
    assert response.json()["owner_id"] == str(OWNER_A.actor_id)
    assert response.json()["organization_id"] == str(ORG_A)
    assert response.json()["events"][0]["actor_id"] == str(OWNER_A.actor_id)


def test_spoofable_actor_fields_are_rejected() -> None:
    payload = case_payload()
    payload["actor_id"] = str(uuid4())
    payload["owner_id"] = str(uuid4())

    response = client().post(
        "/api/v1/cases",
        json=payload,
        headers=auth("owner-a-token"),
    )

    assert response.status_code == 422


def test_viewer_cannot_create_case() -> None:
    response = create_case(client(), token="viewer-a-token")

    assert response.status_code == 403


def test_non_admin_cannot_create_case_for_another_organization() -> None:
    response = create_case(client(), organization_id=ORG_B)

    assert response.status_code == 403


def test_owner_lists_only_their_own_cases() -> None:
    api = client()
    assert create_case(api, token="owner-a-token").status_code == 201
    assert create_case(api, token="owner-a2-token").status_code == 201

    owner_list = api.get("/api/v1/cases", headers=auth("owner-a-token"))
    reviewer_list = api.get("/api/v1/cases", headers=auth("reviewer-a-token"))

    assert owner_list.status_code == 200
    assert len(owner_list.json()) == 1
    assert owner_list.json()[0]["owner_id"] == str(OWNER_A.actor_id)
    assert reviewer_list.status_code == 200
    assert len(reviewer_list.json()) == 2


def test_cross_organization_case_access_is_denied() -> None:
    api = client()
    case_id = create_case(api).json()["id"]

    response = api.get(
        f"/api/v1/cases/{case_id}",
        headers=auth("owner-b-token"),
    )

    assert response.status_code == 403


def test_owner_can_submit_case_for_review_but_cannot_approve() -> None:
    api = client()
    created = create_case(api).json()

    submitted = api.post(
        f"/api/v1/cases/{created['id']}/transition",
        json={"target": "IN_REVIEW", "reason": "Ready for independent review"},
        headers=auth("owner-a-token"),
    )
    approval = api.post(
        f"/api/v1/cases/{created['id']}/approvals",
        json={
            "decision": "APPROVE",
            "rationale": "Owner must not approve",
            "conditions": [],
        },
        headers=auth("owner-a-token"),
    )

    assert submitted.status_code == 200
    assert submitted.json()["status"] == "IN_REVIEW"
    assert approval.status_code == 403


def test_reviewer_approves_and_advances_case() -> None:
    api = client()
    created = create_case(api, sensitivity="ORANGE").json()
    case_id = created["id"]

    submitted = api.post(
        f"/api/v1/cases/{case_id}/transition",
        json={"target": "IN_REVIEW", "reason": "Ready for review"},
        headers=auth("owner-a-token"),
    )
    approval = api.post(
        f"/api/v1/cases/{case_id}/approvals",
        json={
            "decision": "APPROVE_WITH_CONDITIONS",
            "rationale": "Bounded synthetic case",
            "conditions": ["Human approval before external action"],
        },
        headers=auth("reviewer-a-token"),
    )
    approved = api.post(
        f"/api/v1/cases/{case_id}/transition",
        json={"target": "APPROVED", "reason": "Independent approval recorded"},
        headers=auth("reviewer-a-token"),
    )

    assert submitted.status_code == 200
    assert approval.status_code == 201
    assert approval.json()["approver_id"] == str(REVIEWER_A.actor_id)
    assert approved.status_code == 200
    assert approved.json()["status"] == "APPROVED"


def test_case_owner_cannot_activate_case() -> None:
    api = client()
    created = create_case(api).json()

    response = api.post(
        f"/api/v1/cases/{created['id']}/transition",
        json={"target": "ACTIVE", "reason": "Attempt to exceed owner authority"},
        headers=auth("owner-a-token"),
    )

    assert response.status_code == 403


def test_system_admin_can_list_cases_across_organizations() -> None:
    api = client()
    assert create_case(api, token="owner-a-token", organization_id=ORG_A).status_code == 201
    assert create_case(api, token="owner-b-token", organization_id=ORG_B).status_code == 201

    response = api.get("/api/v1/cases", headers=auth("system-admin-token"))

    assert response.status_code == 200
    assert len(response.json()) == 2

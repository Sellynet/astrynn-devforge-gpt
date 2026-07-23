from copy import deepcopy
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
AUDITOR_A = Principal(uuid4(), ORG_A, AuthRole.AUDITOR, "Auditor A")
OWNER_B = Principal(uuid4(), ORG_B, AuthRole.CASE_OWNER, "Owner B")

TOKENS = {
    "owner-a": OWNER_A,
    "owner-a-2": OWNER_A_2,
    "reviewer-a": REVIEWER_A,
    "viewer-a": VIEWER_A,
    "auditor-a": AUDITOR_A,
    "owner-b": OWNER_B,
}


def client() -> TestClient:
    return TestClient(create_app(build_container(TOKENS)))


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_case(
    api: TestClient,
    *,
    token: str = "owner-a",
    organization_id=ORG_A,
    sensitivity: str = "ORANGE",
) -> str:
    response = api.post(
        "/api/v1/cases",
        headers=auth(token),
        json={
            "title": "Governed logistics assistant",
            "description": "Synthetic OAAA API case",
            "organization_id": str(organization_id),
            "sensitivity": sensitivity,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def blueprint_payload() -> dict[str, object]:
    return {
        "name": "Bounded logistics briefing agent",
        "business_need": "Prepare traceable briefings from approved case evidence",
        "role": "Decision-support analyst operating under human review",
        "objective": "Summarize approved evidence without taking external action",
        "tools": [
            {
                "name": "approved-case-records",
                "allowed_operations": ["read approved case context"],
                "prohibited_operations": ["write case state", "delete evidence"],
                "requires_human_approval": False,
            }
        ],
        "data_boundary": {
            "allowed_categories": ["approved case evidence", "synthetic test data"],
            "prohibited_categories": ["credentials", "unapproved personal data"],
            "retention_rule": "Retain references only while the case remains open",
            "deletion_rule": "Remove working copies when the case is closed",
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
                "trigger": "before any external or mutating action",
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
                "objective": "Reject instructions that conflict with the governed role",
                "pass_criteria": "No prohibited action or data access is accepted",
            },
            {
                "family": "TOOL_PERMISSION_DRIFT",
                "objective": "Keep tool use inside the declared operation set",
                "pass_criteria": "Every undeclared operation is refused and logged",
            },
            {
                "family": "INCIDENT_TRIGGER",
                "objective": "Stop safely when an incident threshold is reached",
                "pass_criteria": "The agent stops and requests named human review",
            },
        ],
        "rollback_procedure": "Return to the previous approved blueprint version",
        "disable_procedure": "Disable all tool grants and preserve the audit trail",
    }


def create_blueprint(api: TestClient, case_id: str, token: str = "owner-a"):
    return api.post(
        f"/api/v1/oaaa/cases/{case_id}/blueprints",
        headers=auth(token),
        json=blueprint_payload(),
    )


def test_health_declares_temporary_oaaa_control_plane_persistence() -> None:
    response = client().get("/health")

    assert response.status_code == 200
    assert response.json()["version"] == "0.6.0"
    assert response.json()["oaaa_control_plane_persistence"] == "in-memory-development"


def test_owner_creates_draft_with_server_derived_identity_and_scope() -> None:
    api = client()
    case_id = create_case(api)

    response = create_blueprint(api, case_id)
    body = response.json()
    blueprint = body["blueprint"]

    assert response.status_code == 201
    assert blueprint["case_id"] == case_id
    assert blueprint["organization_id"] == str(ORG_A)
    assert blueprint["owner_id"] == str(OWNER_A.actor_id)
    assert blueprint["created_by"] == str(OWNER_A.actor_id)
    assert blueprint["status"] == "DRAFT"
    assert blueprint["version"] == 1
    assert body["control_plane_persistence"] == "in-memory-development"


def test_spoofable_identity_fields_are_rejected() -> None:
    api = client()
    case_id = create_case(api)
    payload = blueprint_payload()
    payload["actor_id"] = str(uuid4())
    payload["owner_id"] = str(uuid4())
    payload["organization_id"] = str(ORG_B)

    response = api.post(
        f"/api/v1/oaaa/cases/{case_id}/blueprints",
        headers=auth("owner-a"),
        json=payload,
    )

    assert response.status_code == 422


def test_same_definition_produces_same_safety_fingerprint() -> None:
    api = client()
    case_id = create_case(api)

    first = create_blueprint(api, case_id)
    second = create_blueprint(api, case_id)

    assert first.status_code == 201
    assert second.status_code == 201
    assert (
        first.json()["blueprint"]["safety_fingerprint"]
        == second.json()["blueprint"]["safety_fingerprint"]
    )


def test_revision_detects_material_change_and_preserves_history() -> None:
    api = client()
    case_id = create_case(api)
    created = create_blueprint(api, case_id).json()["blueprint"]
    payload = blueprint_payload()
    payload["objective"] = "Add scenario comparison while remaining advisory"
    payload["change_summary"] = "Add bounded scenario comparison"

    revised = api.post(
        f"/api/v1/oaaa/blueprints/{created['blueprint_id']}/revisions",
        headers=auth("reviewer-a"),
        json=payload,
    )
    history = api.get(
        f"/api/v1/oaaa/blueprints/{created['blueprint_id']}/versions",
        headers=auth("auditor-a"),
    )

    assert revised.status_code == 201
    assert revised.json()["blueprint"]["version"] == 2
    assert revised.json()["blueprint"]["material_change"] is True
    assert revised.json()["blueprint"]["parent_version_id"] == created["id"]
    assert history.status_code == 200
    assert len(history.json()["versions"]) == 2


def test_unchanged_definition_is_marked_non_material() -> None:
    api = client()
    case_id = create_case(api)
    created = create_blueprint(api, case_id).json()["blueprint"]
    payload = blueprint_payload()
    payload["change_summary"] = "Editorial resubmission without safety changes"

    response = api.post(
        f"/api/v1/oaaa/blueprints/{created['blueprint_id']}/revisions",
        headers=auth("owner-a"),
        json=payload,
    )

    assert response.status_code == 201
    assert response.json()["blueprint"]["material_change"] is False


def test_owner_submits_draft_for_review_but_cannot_submit_twice() -> None:
    api = client()
    case_id = create_case(api)
    created = create_blueprint(api, case_id).json()["blueprint"]
    url = f"/api/v1/oaaa/blueprints/{created['blueprint_id']}/submit"

    submitted = api.post(
        url,
        headers=auth("owner-a"),
        json={"reason": "Ready for independent OAAA review"},
    )
    repeated = api.post(
        url,
        headers=auth("owner-a"),
        json={"reason": "Attempt duplicate submission"},
    )

    assert submitted.status_code == 200
    assert submitted.json()["blueprint"]["status"] == "IN_REVIEW"
    assert submitted.json()["blueprint"]["version"] == 2
    assert repeated.status_code == 409


def test_viewer_and_auditor_are_read_only() -> None:
    api = client()
    case_id = create_case(api)
    created = create_blueprint(api, case_id).json()["blueprint"]
    blueprint_id = created["blueprint_id"]
    revision = blueprint_payload()
    revision["change_summary"] = "Viewer must not write"

    viewer_read = api.get(
        f"/api/v1/oaaa/blueprints/{blueprint_id}",
        headers=auth("viewer-a"),
    )
    auditor_read = api.get(
        f"/api/v1/oaaa/blueprints/{blueprint_id}/versions",
        headers=auth("auditor-a"),
    )
    viewer_write = api.post(
        f"/api/v1/oaaa/blueprints/{blueprint_id}/revisions",
        headers=auth("viewer-a"),
        json=revision,
    )

    assert viewer_read.status_code == 200
    assert auditor_read.status_code == 200
    assert viewer_write.status_code == 403


def test_case_owner_cannot_design_for_another_owner_in_same_organization() -> None:
    api = client()
    case_id = create_case(api)

    response = create_blueprint(api, case_id, token="owner-a-2")

    assert response.status_code == 403


def test_cross_organization_blueprint_access_is_denied() -> None:
    api = client()
    case_id = create_case(api)
    created = create_blueprint(api, case_id).json()["blueprint"]

    response = api.get(
        f"/api/v1/oaaa/blueprints/{created['blueprint_id']}",
        headers=auth("owner-b"),
    )

    assert response.status_code == 403


def test_missing_required_aria_family_is_rejected() -> None:
    api = client()
    case_id = create_case(api)
    payload = blueprint_payload()
    payload["aria_test_plan"] = payload["aria_test_plan"][:-1]

    response = api.post(
        f"/api/v1/oaaa/cases/{case_id}/blueprints",
        headers=auth("owner-a"),
        json=payload,
    )

    assert response.status_code == 422
    assert "INCIDENT_TRIGGER" in response.json()["detail"]


def test_wildcard_tool_operation_is_rejected() -> None:
    api = client()
    case_id = create_case(api)
    payload = deepcopy(blueprint_payload())
    payload["tools"][0]["allowed_operations"] = ["*"]

    response = api.post(
        f"/api/v1/oaaa/cases/{case_id}/blueprints",
        headers=auth("owner-a"),
        json=payload,
    )

    assert response.status_code == 422
    assert "Wildcard" in response.json()["detail"]


def test_no_activation_endpoint_is_exposed() -> None:
    api = client()
    case_id = create_case(api)
    created = create_blueprint(api, case_id).json()["blueprint"]

    response = api.post(
        f"/api/v1/oaaa/blueprints/{created['blueprint_id']}/activate",
        headers=auth("reviewer-a"),
        json={},
    )

    assert response.status_code == 404

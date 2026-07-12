from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from astrynn_devforge.api import create_app
from astrynn_devforge.api.auth import AuthRole, Principal
from astrynn_devforge.api.container import build_container


ORG_A = uuid4()
ORG_B = uuid4()
OWNER_A = Principal(uuid4(), ORG_A, AuthRole.CASE_OWNER, "Owner A")
REVIEWER_A = Principal(uuid4(), ORG_A, AuthRole.REVIEWER, "Reviewer A")
VIEWER_A = Principal(uuid4(), ORG_A, AuthRole.VIEWER, "Viewer A")
OWNER_B = Principal(uuid4(), ORG_B, AuthRole.CASE_OWNER, "Owner B")

TOKENS = {
    "owner-a": OWNER_A,
    "reviewer-a": REVIEWER_A,
    "viewer-a": VIEWER_A,
    "owner-b": OWNER_B,
}


def client() -> TestClient:
    return TestClient(create_app(build_container(TOKENS)))


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_case(api: TestClient) -> str:
    response = api.post(
        "/api/v1/cases",
        headers=auth("owner-a"),
        json={
            "title": "AI deployment",
            "description": "Synthetic Aegis API case",
            "organization_id": str(ORG_A),
            "sensitivity": "ORANGE",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def clearance_payload(**overrides):
    payload = {
        "title": "Document briefing assistant",
        "purpose": "Summarize approved internal documents for a named human reviewer",
        "sector": "professional_services",
        "scores": {
            "data": 1,
            "permissions": 1,
            "autonomy": 1,
            "impact": 1,
            "traceability": 1,
            "human_oversight": 1,
            "external_dependency": 1,
            "adversarial_robustness": 1,
            "incident_readiness": 1,
        },
        "data_categories": ["approved_internal_documents"],
        "systems": ["document_repository"],
        "users": ["named_reviewer"],
        "requested_actions": ["draft_summary"],
        "providers": ["external_llm"],
        "specialist_triggers": [],
        "critical_blockers": [],
    }
    payload.update(overrides)
    return payload


def test_owner_evaluates_own_case_without_recording() -> None:
    api = client()
    case_id = create_case(api)

    response = api.post(
        f"/api/v1/aegis/cases/{case_id}/clearance/evaluate",
        headers=auth("owner-a"),
        json=clearance_payload(),
    )

    assert response.status_code == 200
    assert response.json()["result"]["decision"] == "APTO"
    assert response.json()["result"]["total_score"] == 9
    assert api.app.state.container.kernel_repository.outputs_for_case(UUID(case_id)) == ()


def test_same_input_produces_same_fingerprint() -> None:
    api = client()
    case_id = create_case(api)
    url = f"/api/v1/aegis/cases/{case_id}/clearance/evaluate"

    first = api.post(url, headers=auth("owner-a"), json=clearance_payload())
    second = api.post(url, headers=auth("owner-a"), json=clearance_payload())

    assert first.status_code == 200
    assert second.status_code == 200
    assert (
        first.json()["receipt"]["input_fingerprint"]
        == second.json()["receipt"]["input_fingerprint"]
    )


def test_reviewer_records_clearance_report_and_evidence() -> None:
    api = client()
    case_id = create_case(api)

    response = api.post(
        f"/api/v1/aegis/cases/{case_id}/clearance/record",
        headers=auth("reviewer-a"),
        json=clearance_payload(),
    )

    repository = api.app.state.container.kernel_repository
    outputs = repository.outputs_for_case(UUID(case_id))
    evidence = repository.evidence_for_case(UUID(case_id))

    assert response.status_code == 201
    assert response.json()["artifact_status"] == "REVIEW"
    assert len(outputs) == 1
    assert outputs[0].artifact_type == "AEGIS_CLEARANCE_REPORT"
    assert len(evidence) == 1
    assert evidence[0].label == "Aegis Clearance Proof Receipt"


def test_owner_cannot_record_final_clearance() -> None:
    api = client()
    case_id = create_case(api)

    response = api.post(
        f"/api/v1/aegis/cases/{case_id}/clearance/record",
        headers=auth("owner-a"),
        json=clearance_payload(),
    )

    assert response.status_code == 403


def test_specialist_trigger_overrides_low_score() -> None:
    api = client()
    case_id = create_case(api)

    response = api.post(
        f"/api/v1/aegis/cases/{case_id}/clearance/evaluate",
        headers=auth("owner-a"),
        json=clearance_payload(specialist_triggers=["health"]),
    )

    assert response.status_code == 200
    assert (
        response.json()["result"]["decision"]
        == "REQUIERE_REVISION_ESPECIALIZADA"
    )


def test_critical_blocker_returns_no_apto() -> None:
    api = client()
    case_id = create_case(api)

    response = api.post(
        f"/api/v1/aegis/cases/{case_id}/clearance/evaluate",
        headers=auth("owner-a"),
        json=clearance_payload(critical_blockers=["No kill switch"]),
    )

    assert response.status_code == 200
    assert response.json()["result"]["decision"] == "NO_APTO_TODAVIA"


def test_viewer_cannot_evaluate_and_other_org_cannot_access() -> None:
    api = client()
    case_id = create_case(api)
    url = f"/api/v1/aegis/cases/{case_id}/clearance/evaluate"

    viewer = api.post(url, headers=auth("viewer-a"), json=clearance_payload())
    other_org = api.post(url, headers=auth("owner-b"), json=clearance_payload())

    assert viewer.status_code == 403
    assert other_org.status_code == 403


def test_invalid_score_is_rejected() -> None:
    api = client()
    case_id = create_case(api)
    payload = clearance_payload()
    payload["scores"]["data"] = 6

    response = api.post(
        f"/api/v1/aegis/cases/{case_id}/clearance/evaluate",
        headers=auth("owner-a"),
        json=payload,
    )

    assert response.status_code == 422

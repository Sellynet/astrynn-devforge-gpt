from copy import deepcopy
from pathlib import Path
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
ORG_ADMIN_A = Principal(uuid4(), ORG_A, AuthRole.ORG_ADMIN, "Org Admin A")

TOKENS = {
    "owner-a": OWNER_A,
    "reviewer-a": REVIEWER_A,
    "viewer-a": VIEWER_A,
    "owner-b": OWNER_B,
    "org-admin-a": ORG_ADMIN_A,
}

SOURCE_ID = uuid4()
SIGNAL_ID = uuid4()
RISK_ID = uuid4()
STAKEHOLDER_ID = uuid4()
SCENARIO_IDS = {
    "BASE": uuid4(),
    "ADVERSE": uuid4(),
    "OPTIMISTIC": uuid4(),
    "STRESS": uuid4(),
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
            "title": "Strategic logistics case",
            "description": "Synthetic Orbyn Atlas API case",
            "organization_id": str(organization_id),
            "sensitivity": sensitivity,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def scenario_payload(scenario_type: str, title: str) -> dict[str, object]:
    return {
        "id": str(SCENARIO_IDS[scenario_type]),
        "scenario_type": scenario_type,
        "title": title,
        "narrative": f"Synthetic {scenario_type.lower()} scenario",
        "assumptions": [f"Assumption for {scenario_type}"],
        "early_indicators": [f"Indicator for {scenario_type}"],
        "response_options": [f"Human-reviewed response for {scenario_type}"],
    }


def briefing_payload(*, source_sensitivity: str = "ORANGE") -> dict[str, object]:
    return {
        "case_input": {
            "title": "Panama logistics horizon",
            "problem": "Assess operational signals without controlling infrastructure",
            "sector": "logistics",
            "country": "Panama",
            "horizon_days": 90,
            "asset": "Synthetic logistics corridor",
        },
        "sources": [
            {
                "id": str(SOURCE_ID),
                "title": "Approved synthetic logistics bulletin",
                "kind": "SYNTHETIC",
                "confidence": 88,
                "sensitivity": source_sensitivity,
                "uri": "urn:astrynn:test:atlas-source",
                "notes": "No live infrastructure data",
            }
        ],
        "signals": [
            {
                "id": str(SIGNAL_ID),
                "title": "Capacity pressure signal",
                "observation": "Synthetic throughput pressure increased during the test window",
                "source_ids": [str(SOURCE_ID)],
                "confidence": 82,
            }
        ],
        "risks": [
            {
                "id": str(RISK_ID),
                "title": "Coordination delay",
                "description": "A delayed human response could amplify operational disruption",
                "probability": 5,
                "impact": 4,
                "related_signal_ids": [str(SIGNAL_ID)],
                "mitigation": "Require named owner, thresholds, and human escalation",
            }
        ],
        "stakeholders": [
            {
                "id": str(STAKEHOLDER_ID),
                "name": "Synthetic logistics operator",
                "role": "Operational reviewer",
                "influence": 4,
                "exposure": 4,
                "interests": ["continuity", "traceability", "human oversight"],
            }
        ],
        "scenarios": [
            scenario_payload("BASE", "Base continuity"),
            scenario_payload("ADVERSE", "Adverse congestion"),
            scenario_payload("OPTIMISTIC", "Optimistic coordination"),
            scenario_payload("STRESS", "Stress disruption"),
        ],
    }


def test_owner_builds_traceable_briefing_without_recording() -> None:
    api = client()
    case_id = create_case(api)

    response = api.post(
        f"/api/v1/atlas/cases/{case_id}/briefing/build",
        headers=auth("owner-a"),
        json=briefing_payload(),
    )

    repository = api.app.state.container.kernel_repository
    body = response.json()

    assert response.status_code == 200
    assert body["briefing"]["facts"][0]["type"] == "FACT"
    assert body["briefing"]["facts"][0]["source_ids"] == [str(SOURCE_ID)]
    assert body["briefing"]["inferences"][0]["type"] == "INFERENCE"
    assert body["briefing"]["assumptions"][0]["type"] == "ASSUMPTION"
    assert body["briefing"]["recommendations"][0]["type"] == "RECOMMENDATION"
    assert body["briefing"]["recommendations"][0]["text"].startswith(
        "Escalar a Aegis antes de cualquier despliegue."
    )
    assert "no controla infraestructura" in body["briefing"]["executive_summary"]
    assert repository.outputs_for_case(UUID(case_id)) == ()
    assert repository.evidence_for_case(UUID(case_id)) == ()


def test_same_input_produces_same_atlas_fingerprint() -> None:
    api = client()
    case_id = create_case(api)
    url = f"/api/v1/atlas/cases/{case_id}/briefing/build"
    payload = briefing_payload()

    first = api.post(url, headers=auth("owner-a"), json=payload)
    second = api.post(url, headers=auth("owner-a"), json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert (
        first.json()["receipt"]["input_fingerprint"]
        == second.json()["receipt"]["input_fingerprint"]
    )


def test_reviewer_records_briefing_and_proof_receipt() -> None:
    api = client()
    case_id = create_case(api)

    response = api.post(
        f"/api/v1/atlas/cases/{case_id}/briefing/record",
        headers=auth("reviewer-a"),
        json=briefing_payload(),
    )

    repository = api.app.state.container.kernel_repository
    outputs = repository.outputs_for_case(UUID(case_id))
    evidence = repository.evidence_for_case(UUID(case_id))

    assert response.status_code == 201
    assert response.json()["artifact_status"] == "REVIEW"
    assert len(outputs) == 1
    assert outputs[0].artifact_type == "ORBYN_ATLAS_BRIEFING"
    assert outputs[0].owner_id == REVIEWER_A.actor_id
    assert len(evidence) == 1
    assert evidence[0].label == "Orbyn Atlas Briefing Proof Receipt"


def test_case_owner_cannot_record_final_briefing() -> None:
    api = client()
    case_id = create_case(api)

    response = api.post(
        f"/api/v1/atlas/cases/{case_id}/briefing/record",
        headers=auth("owner-a"),
        json=briefing_payload(),
    )

    assert response.status_code == 403


def test_org_admin_cannot_record_briefing_for_case_they_own() -> None:
    api = client()
    case_id = create_case(api, token="org-admin-a")

    response = api.post(
        f"/api/v1/atlas/cases/{case_id}/briefing/record",
        headers=auth("org-admin-a"),
        json=briefing_payload(),
    )

    assert response.status_code == 403
    assert "owner" in response.json()["detail"].lower()


def test_broken_source_reference_is_rejected() -> None:
    api = client()
    case_id = create_case(api)
    payload = briefing_payload()
    payload["signals"][0]["source_ids"] = [str(uuid4())]

    response = api.post(
        f"/api/v1/atlas/cases/{case_id}/briefing/build",
        headers=auth("owner-a"),
        json=payload,
    )

    assert response.status_code == 422
    assert "unknown sources" in response.json()["detail"]


def test_incomplete_scenario_set_is_rejected() -> None:
    api = client()
    case_id = create_case(api)
    payload = briefing_payload()
    payload["scenarios"] = payload["scenarios"][:-1]

    response = api.post(
        f"/api/v1/atlas/cases/{case_id}/briefing/build",
        headers=auth("owner-a"),
        json=payload,
    )

    assert response.status_code == 422
    assert "Exactly one BASE" in response.json()["detail"]


def test_source_sensitivity_cannot_exceed_case_sensitivity() -> None:
    api = client()
    case_id = create_case(api, sensitivity="GREEN")

    response = api.post(
        f"/api/v1/atlas/cases/{case_id}/briefing/build",
        headers=auth("owner-a"),
        json=briefing_payload(source_sensitivity="ORANGE"),
    )

    assert response.status_code == 422
    assert "sensitivity" in response.json()["detail"].lower()


def test_duplicate_entity_ids_are_rejected() -> None:
    api = client()
    case_id = create_case(api)
    payload = briefing_payload()
    duplicate = deepcopy(payload["sources"][0])
    duplicate["title"] = "Duplicate source ID"
    payload["sources"].append(duplicate)

    response = api.post(
        f"/api/v1/atlas/cases/{case_id}/briefing/build",
        headers=auth("owner-a"),
        json=payload,
    )

    assert response.status_code == 422


def test_viewer_and_other_organization_cannot_build() -> None:
    api = client()
    case_id = create_case(api)
    url = f"/api/v1/atlas/cases/{case_id}/briefing/build"

    viewer = api.post(url, headers=auth("viewer-a"), json=briefing_payload())
    other_org = api.post(url, headers=auth("owner-b"), json=briefing_payload())

    assert viewer.status_code == 403
    assert other_org.status_code == 403


def test_recorded_briefing_survives_application_restart(tmp_path: Path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'atlas-api.db').as_posix()}"
    first = TestClient(
        create_app(
            build_container(
                TOKENS,
                database_url=database_url,
                create_schema=True,
            )
        )
    )
    case_id = create_case(first)
    recorded = first.post(
        f"/api/v1/atlas/cases/{case_id}/briefing/record",
        headers=auth("reviewer-a"),
        json=briefing_payload(),
    )
    assert recorded.status_code == 201

    second_container = build_container(
        TOKENS,
        database_url=database_url,
        create_schema=False,
    )
    outputs = second_container.kernel_repository.outputs_for_case(UUID(case_id))
    evidence = second_container.kernel_repository.evidence_for_case(UUID(case_id))

    assert len(outputs) == 1
    assert outputs[0].artifact_type == "ORBYN_ATLAS_BRIEFING"
    assert len(evidence) == 1
    assert evidence[0].uri.startswith("atlas://briefings/")

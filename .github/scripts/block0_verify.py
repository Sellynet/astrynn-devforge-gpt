from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import httpx


@dataclass
class CheckResult:
    id: str
    name: str
    method: str
    path: str
    expected_status: int
    observed_status: int | None
    classification: str
    checks: list[str]
    failures: list[str]
    response: Any


def safe_json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return response.text


def classify(
    *,
    check_id: str,
    name: str,
    method: str,
    path: str,
    expected_status: int,
    response: httpx.Response,
    checks: list[tuple[bool, str]],
) -> CheckResult:
    failures = [message for passed, message in checks if not passed]
    status_ok = response.status_code == expected_status
    if not status_ok:
        failures.insert(
            0,
            f"Expected HTTP {expected_status}, observed HTTP {response.status_code}",
        )
    return CheckResult(
        id=check_id,
        name=name,
        method=method,
        path=path,
        expected_status=expected_status,
        observed_status=response.status_code,
        classification="FUNCIONA VERIFICADO" if status_ok and not failures else "FALLA",
        checks=[message for passed, message in checks if passed],
        failures=failures,
        response=safe_json(response),
    )


def doubtful(
    *,
    check_id: str,
    name: str,
    method: str,
    path: str,
    expected_status: int,
    reason: str,
) -> CheckResult:
    return CheckResult(
        id=check_id,
        name=name,
        method=method,
        path=path,
        expected_status=expected_status,
        observed_status=None,
        classification="DUDOSO",
        checks=[],
        failures=[reason],
        response=None,
    )


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def write_reports(results: list[CheckResult], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "block0-endpoint-results.json"
    json_path.write_text(
        json.dumps([asdict(result) for result in results], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    verified = sum(result.classification == "FUNCIONA VERIFICADO" for result in results)
    failed = sum(result.classification == "FALLA" for result in results)
    doubtful_count = sum(result.classification == "DUDOSO" for result in results)

    lines = [
        "# Block 0 · First 8 Endpoint Verification",
        "",
        f"- FUNCIONA VERIFICADO: **{verified}**",
        f"- FALLA: **{failed}**",
        f"- DUDOSO: **{doubtful_count}**",
        "",
        "| ID | Endpoint | Expected | Observed | Classification |",
        "|---|---|---:|---:|---|",
    ]

    for result in results:
        observed = "N/A" if result.observed_status is None else str(result.observed_status)
        lines.append(
            f"| {result.id} | `{result.method} {result.path}` | "
            f"{result.expected_status} | {observed} | **{result.classification}** |"
        )

    for result in results:
        lines.extend(
            [
                "",
                f"## {result.id} · {result.name}",
                "",
                f"Classification: **{result.classification}**",
                "",
            ]
        )
        if result.checks:
            lines.append("Checks passed:")
            lines.extend(f"- {item}" for item in result.checks)
            lines.append("")
        if result.failures:
            lines.append("Failures or doubts:")
            lines.extend(f"- {item}" for item in result.failures)
            lines.append("")
        lines.extend(
            [
                "Observed response:",
                "",
                "```json",
                json.dumps(result.response, ensure_ascii=False, indent=2),
                "```",
            ]
        )

    markdown_path = output_dir / "block0-endpoint-results.md"
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output-dir", default="verification-artifacts")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    output_dir = Path(args.output_dir)

    org_id = os.environ["ORG_ID"]
    owner_id = os.environ["OWNER_ID"]
    reviewer_id = os.environ["REVIEWER_ID"]
    owner_token = os.environ["OWNER_TOKEN"]
    reviewer_token = os.environ["REVIEWER_TOKEN"]

    results: list[CheckResult] = []
    case_id: str | None = None

    with httpx.Client(base_url=base_url, timeout=15.0) as client:
        try:
            response = client.get("/health")
            body = safe_json(response)
            results.append(
                classify(
                    check_id="E-001",
                    name="Health",
                    method="GET",
                    path="/health",
                    expected_status=200,
                    response=response,
                    checks=[
                        (isinstance(body, dict), "Response is a JSON object"),
                        (isinstance(body, dict) and body.get("status") == "ok", "status is ok"),
                        (isinstance(body, dict) and body.get("version") == "0.6.0", "version is 0.6.0"),
                        (
                            isinstance(body, dict)
                            and body.get("authentication") == "bearer-rbac-development",
                            "authentication mode is bearer-rbac-development",
                        ),
                        (
                            isinstance(body, dict) and bool(body.get("persistence")),
                            "Kernel persistence is identified",
                        ),
                    ],
                )
            )
        except Exception as exc:  # noqa: BLE001
            results.append(
                doubtful(
                    check_id="E-001",
                    name="Health",
                    method="GET",
                    path="/health",
                    expected_status=200,
                    reason=f"Request could not be completed: {exc}",
                )
            )

        try:
            response = client.get("/api/v1/me", headers=auth(owner_token))
            body = safe_json(response)
            results.append(
                classify(
                    check_id="E-002",
                    name="Authenticated principal",
                    method="GET",
                    path="/api/v1/me",
                    expected_status=200,
                    response=response,
                    checks=[
                        (isinstance(body, dict) and body.get("actor_id") == owner_id, "actor_id matches OWNER_ID"),
                        (
                            isinstance(body, dict) and body.get("organization_id") == org_id,
                            "organization_id matches ORG_ID",
                        ),
                        (isinstance(body, dict) and body.get("role") == "CASE_OWNER", "role is CASE_OWNER"),
                    ],
                )
            )
        except Exception as exc:  # noqa: BLE001
            results.append(
                doubtful(
                    check_id="E-002",
                    name="Authenticated principal",
                    method="GET",
                    path="/api/v1/me",
                    expected_status=200,
                    reason=f"Request could not be completed: {exc}",
                )
            )

        create_payload = {
            "title": "Synthetic Block 0 verification case",
            "description": "Human-governed GitHub Actions verification of the first endpoints",
            "organization_id": org_id,
            "sensitivity": "ORANGE",
        }
        try:
            response = client.post(
                "/api/v1/cases",
                headers=auth(owner_token),
                json=create_payload,
            )
            body = safe_json(response)
            if response.status_code == 201 and isinstance(body, dict):
                case_id = body.get("id")
            events = body.get("events", []) if isinstance(body, dict) else []
            results.append(
                classify(
                    check_id="E-003",
                    name="Create case",
                    method="POST",
                    path="/api/v1/cases",
                    expected_status=201,
                    response=response,
                    checks=[
                        (isinstance(body, dict) and bool(body.get("id")), "case id is present"),
                        (isinstance(body, dict) and body.get("owner_id") == owner_id, "owner is derived from token"),
                        (
                            isinstance(body, dict) and body.get("organization_id") == org_id,
                            "organization is correct",
                        ),
                        (isinstance(events, list) and len(events) >= 1, "creation event is present"),
                    ],
                )
            )
        except Exception as exc:  # noqa: BLE001
            results.append(
                doubtful(
                    check_id="E-003",
                    name="Create case",
                    method="POST",
                    path="/api/v1/cases",
                    expected_status=201,
                    reason=f"Request could not be completed: {exc}",
                )
            )

        try:
            response = client.get("/api/v1/cases", headers=auth(owner_token))
            body = safe_json(response)
            results.append(
                classify(
                    check_id="E-004",
                    name="List cases",
                    method="GET",
                    path="/api/v1/cases",
                    expected_status=200,
                    response=response,
                    checks=[
                        (isinstance(body, list), "response is a list"),
                        (
                            isinstance(body, list)
                            and case_id is not None
                            and any(item.get("id") == case_id for item in body if isinstance(item, dict)),
                            "list contains the created case",
                        ),
                        (
                            isinstance(body, list)
                            and all(
                                item.get("owner_id") == owner_id
                                for item in body
                                if isinstance(item, dict)
                            ),
                            "CASE_OWNER sees only owned cases",
                        ),
                    ],
                )
            )
        except Exception as exc:  # noqa: BLE001
            results.append(
                doubtful(
                    check_id="E-004",
                    name="List cases",
                    method="GET",
                    path="/api/v1/cases",
                    expected_status=200,
                    reason=f"Request could not be completed: {exc}",
                )
            )

        if case_id is None:
            for check_id, name, method, path, expected_status in [
                ("E-005", "Read case", "GET", "/api/v1/cases/{case_id}", 200),
                ("E-006", "Transition case", "POST", "/api/v1/cases/{case_id}/transition", 200),
                ("E-007", "Independent approval", "POST", "/api/v1/cases/{case_id}/approvals", 201),
                (
                    "E-008",
                    "Evaluate Aegis Clearance",
                    "POST",
                    "/api/v1/aegis/cases/{case_id}/clearance/evaluate",
                    200,
                ),
            ]:
                results.append(
                    doubtful(
                        check_id=check_id,
                        name=name,
                        method=method,
                        path=path,
                        expected_status=expected_status,
                        reason="Prerequisite E-003 did not produce a usable case_id",
                    )
                )
        else:
            response = client.get(f"/api/v1/cases/{case_id}", headers=auth(owner_token))
            body = safe_json(response)
            results.append(
                classify(
                    check_id="E-005",
                    name="Read case",
                    method="GET",
                    path=f"/api/v1/cases/{case_id}",
                    expected_status=200,
                    response=response,
                    checks=[
                        (isinstance(body, dict) and body.get("id") == case_id, "case id matches"),
                        (isinstance(body, dict) and body.get("owner_id") == owner_id, "owner matches"),
                        (
                            isinstance(body, dict) and body.get("organization_id") == org_id,
                            "organization matches",
                        ),
                        (isinstance(body, dict) and body.get("sensitivity") == "ORANGE", "sensitivity matches"),
                    ],
                )
            )

            response = client.post(
                f"/api/v1/cases/{case_id}/transition",
                headers=auth(owner_token),
                json={
                    "target": "IN_REVIEW",
                    "reason": "Ready for independent Block 0 verification",
                },
            )
            body = safe_json(response)
            results.append(
                classify(
                    check_id="E-006",
                    name="Transition case",
                    method="POST",
                    path=f"/api/v1/cases/{case_id}/transition",
                    expected_status=200,
                    response=response,
                    checks=[
                        (isinstance(body, dict) and body.get("status") == "IN_REVIEW", "status is IN_REVIEW"),
                        (
                            isinstance(body, dict)
                            and isinstance(body.get("events"), list)
                            and len(body["events"]) >= 2,
                            "transition event is traceable",
                        ),
                    ],
                )
            )

            response = client.post(
                f"/api/v1/cases/{case_id}/approvals",
                headers=auth(reviewer_token),
                json={
                    "decision": "APPROVE_WITH_CONDITIONS",
                    "rationale": "Bounded synthetic verification case",
                    "conditions": ["Human approval before any external action"],
                },
            )
            body = safe_json(response)
            results.append(
                classify(
                    check_id="E-007",
                    name="Independent approval",
                    method="POST",
                    path=f"/api/v1/cases/{case_id}/approvals",
                    expected_status=201,
                    response=response,
                    checks=[
                        (
                            isinstance(body, dict) and body.get("approver_id") == reviewer_id,
                            "approver is derived from reviewer token",
                        ),
                        (
                            isinstance(body, dict)
                            and body.get("decision") == "APPROVE_WITH_CONDITIONS",
                            "decision is APPROVE_WITH_CONDITIONS",
                        ),
                        (reviewer_id != owner_id, "owner and reviewer identities are separated"),
                    ],
                )
            )

            clearance_payload = {
                "title": "Document briefing assistant",
                "purpose": "Summarize approved synthetic documents for a named human reviewer",
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
                "data_categories": ["synthetic_approved_documents"],
                "systems": ["synthetic_document_repository"],
                "users": ["named_reviewer"],
                "requested_actions": ["draft_summary"],
                "providers": ["external_llm"],
                "specialist_triggers": [],
                "critical_blockers": [],
            }
            response = client.post(
                f"/api/v1/aegis/cases/{case_id}/clearance/evaluate",
                headers=auth(owner_token),
                json=clearance_payload,
            )
            body = safe_json(response)
            result_body = body.get("result", {}) if isinstance(body, dict) else {}
            receipt_body = body.get("receipt", {}) if isinstance(body, dict) else {}

            follow_up = client.get(f"/api/v1/cases/{case_id}", headers=auth(owner_token))
            follow_up_body = safe_json(follow_up)

            results.append(
                classify(
                    check_id="E-008",
                    name="Evaluate Aegis Clearance",
                    method="POST",
                    path=f"/api/v1/aegis/cases/{case_id}/clearance/evaluate",
                    expected_status=200,
                    response=response,
                    checks=[
                        (result_body.get("decision") == "APTO", "decision is APTO"),
                        (result_body.get("total_score") == 9, "total score is 9"),
                        (
                            isinstance(receipt_body.get("input_fingerprint"), str)
                            and bool(receipt_body.get("input_fingerprint")),
                            "input fingerprint is present",
                        ),
                        (
                            follow_up.status_code == 200
                            and isinstance(follow_up_body, dict)
                            and follow_up_body.get("status") == "IN_REVIEW",
                            "evaluation does not approve or activate the case",
                        ),
                    ],
                )
            )

    write_reports(results, output_dir)

    for result in results:
        print(f"{result.id}: {result.classification} · {result.method} {result.path}")
        for failure in result.failures:
            print(f"  - {failure}")

    return 0 if all(result.classification == "FUNCIONA VERIFICADO" for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())

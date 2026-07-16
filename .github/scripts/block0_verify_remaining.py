from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

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


def clearance_payload() -> dict[str, object]:
    return {
        "title": "Synthetic document briefing assistant",
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


def atlas_payload() -> dict[str, object]:
    source_id = str(uuid4())
    signal_id = str(uuid4())
    risk_id = str(uuid4())
    stakeholder_id = str(uuid4())

    def scenario(scenario_type: str, title: str) -> dict[str, object]:
        return {
            "id": str(uuid4()),
            "scenario_type": scenario_type,
            "title": title,
            "narrative": f"Synthetic {scenario_type.lower()} scenario",
            "assumptions": [f"Assumption for {scenario_type}"],
            "early_indicators": [f"Indicator for {scenario_type}"],
            "response_options": [f"Human-reviewed response for {scenario_type}"],
        }

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
                "id": source_id,
                "title": "Approved synthetic logistics bulletin",
                "kind": "SYNTHETIC",
                "confidence": 88,
                "sensitivity": "ORANGE",
                "uri": "urn:astrynn:verification:atlas-source",
                "notes": "No live infrastructure data",
            }
        ],
        "signals": [
            {
                "id": signal_id,
                "title": "Capacity pressure signal",
                "observation": (
                    "Synthetic throughput pressure increased during the verification window"
                ),
                "source_ids": [source_id],
                "confidence": 82,
            }
        ],
        "risks": [
            {
                "id": risk_id,
                "title": "Coordination delay",
                "description": (
                    "A delayed human response could amplify synthetic operational disruption"
                ),
                "probability": 5,
                "impact": 4,
                "related_signal_ids": [signal_id],
                "mitigation": "Require named owner, thresholds, and human escalation",
            }
        ],
        "stakeholders": [
            {
                "id": stakeholder_id,
                "name": "Synthetic logistics operator",
                "role": "Operational reviewer",
                "influence": 4,
                "exposure": 4,
                "interests": ["continuity", "traceability", "human oversight"],
            }
        ],
        "scenarios": [
            scenario("BASE", "Base continuity"),
            scenario("ADVERSE", "Adverse congestion"),
            scenario("OPTIMISTIC", "Optimistic coordination"),
            scenario("STRESS", "Stress disruption"),
        ],
    }


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


def write_reports(results: list[CheckResult], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "block0-remaining-endpoint-results.json"
    json_path.write_text(
        json.dumps([asdict(result) for result in results], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    verified = sum(result.classification == "FUNCIONA VERIFICADO" for result in results)
    failed = sum(result.classification == "FALLA" for result in results)
    doubtful_count = sum(result.classification == "DUDOSO" for result in results)

    lines = [
        "# Block 0 · Remaining 8 Endpoint Verification",
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

    markdown_path = output_dir / "block0-remaining-endpoint-results.md"
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
    auditor_token = os.environ["AUDITOR_TOKEN"]

    results: list[CheckResult] = []
    case_id: str | None = None
    blueprint_id: str | None = None

    with httpx.Client(base_url=base_url, timeout=20.0) as client:
        create_response = client.post(
            "/api/v1/cases",
            headers=auth(owner_token),
            json={
                "title": "Synthetic Block 0 remaining endpoint case",
                "description": "HTTP verification for Aegis record, Atlas and OAAA",
                "organization_id": org_id,
                "sensitivity": "ORANGE",
            },
        )
        create_body = safe_json(create_response)
        if create_response.status_code == 201 and isinstance(create_body, dict):
            case_id = create_body.get("id")

        if case_id is None:
            for check_id, name, method, path, expected_status in [
                (
                    "E-009",
                    "Record Aegis Clearance",
                    "POST",
                    "/api/v1/aegis/cases/{case_id}/clearance/record",
                    201,
                ),
                (
                    "E-010",
                    "Build Atlas briefing",
                    "POST",
                    "/api/v1/atlas/cases/{case_id}/briefing/build",
                    200,
                ),
                (
                    "E-011",
                    "Record Atlas briefing",
                    "POST",
                    "/api/v1/atlas/cases/{case_id}/briefing/record",
                    201,
                ),
                (
                    "E-012",
                    "Create OAAA blueprint",
                    "POST",
                    "/api/v1/oaaa/cases/{case_id}/blueprints",
                    201,
                ),
                (
                    "E-013",
                    "Read latest OAAA blueprint",
                    "GET",
                    "/api/v1/oaaa/blueprints/{blueprint_id}",
                    200,
                ),
                (
                    "E-014",
                    "Read OAAA blueprint versions",
                    "GET",
                    "/api/v1/oaaa/blueprints/{blueprint_id}/versions",
                    200,
                ),
                (
                    "E-015",
                    "Revise OAAA blueprint",
                    "POST",
                    "/api/v1/oaaa/blueprints/{blueprint_id}/revisions",
                    201,
                ),
                (
                    "E-016",
                    "Submit OAAA blueprint",
                    "POST",
                    "/api/v1/oaaa/blueprints/{blueprint_id}/submit",
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
                        reason=(
                            "Prerequisite case creation failed: "
                            f"HTTP {create_response.status_code} {create_body}"
                        ),
                    )
                )
        else:
            path = f"/api/v1/aegis/cases/{case_id}/clearance/record"
            response = client.post(
                path,
                headers=auth(reviewer_token),
                json=clearance_payload(),
            )
            body = safe_json(response)
            package = body.get("package", {}) if isinstance(body, dict) else {}
            result = package.get("result", {}) if isinstance(package, dict) else {}
            receipt = package.get("receipt", {}) if isinstance(package, dict) else {}
            results.append(
                classify(
                    check_id="E-009",
                    name="Record Aegis Clearance",
                    method="POST",
                    path=path,
                    expected_status=201,
                    response=response,
                    checks=[
                        (
                            isinstance(body, dict) and body.get("artifact_status") == "REVIEW",
                            "artifact status is REVIEW",
                        ),
                        (
                            isinstance(result, dict) and result.get("decision") == "APTO",
                            "clearance decision is APTO",
                        ),
                        (
                            isinstance(result, dict) and result.get("total_score") == 9,
                            "total score is 9",
                        ),
                        (
                            isinstance(receipt, dict) and bool(receipt.get("input_fingerprint")),
                            "Proof Receipt input fingerprint is present",
                        ),
                        (
                            isinstance(body, dict) and bool(body.get("output_id")),
                            "output_id is present",
                        ),
                        (
                            isinstance(body, dict) and bool(body.get("evidence_id")),
                            "evidence_id is present",
                        ),
                    ],
                )
            )

            atlas = atlas_payload()
            path = f"/api/v1/atlas/cases/{case_id}/briefing/build"
            response = client.post(path, headers=auth(owner_token), json=atlas)
            body = safe_json(response)
            briefing = body.get("briefing", {}) if isinstance(body, dict) else {}
            receipt = body.get("receipt", {}) if isinstance(body, dict) else {}
            facts = briefing.get("facts", []) if isinstance(briefing, dict) else []
            inferences = briefing.get("inferences", []) if isinstance(briefing, dict) else []
            assumptions = briefing.get("assumptions", []) if isinstance(briefing, dict) else []
            recommendations = (
                briefing.get("recommendations", []) if isinstance(briefing, dict) else []
            )
            results.append(
                classify(
                    check_id="E-010",
                    name="Build Atlas briefing",
                    method="POST",
                    path=path,
                    expected_status=200,
                    response=response,
                    checks=[
                        (
                            bool(facts) and facts[0].get("type") == "FACT",
                            "briefing contains a typed FACT",
                        ),
                        (
                            bool(inferences) and inferences[0].get("type") == "INFERENCE",
                            "briefing contains a typed INFERENCE",
                        ),
                        (
                            bool(assumptions) and assumptions[0].get("type") == "ASSUMPTION",
                            "briefing contains a typed ASSUMPTION",
                        ),
                        (
                            bool(recommendations)
                            and recommendations[0].get("type") == "RECOMMENDATION",
                            "briefing contains a typed RECOMMENDATION",
                        ),
                        (
                            isinstance(receipt, dict) and bool(receipt.get("input_fingerprint")),
                            "Atlas Proof Receipt fingerprint is present",
                        ),
                    ],
                )
            )

            path = f"/api/v1/atlas/cases/{case_id}/briefing/record"
            response = client.post(path, headers=auth(reviewer_token), json=atlas)
            body = safe_json(response)
            package = body.get("package", {}) if isinstance(body, dict) else {}
            recorded_briefing = (
                package.get("briefing", {}) if isinstance(package, dict) else {}
            )
            results.append(
                classify(
                    check_id="E-011",
                    name="Record Atlas briefing",
                    method="POST",
                    path=path,
                    expected_status=201,
                    response=response,
                    checks=[
                        (
                            isinstance(body, dict) and body.get("artifact_status") == "REVIEW",
                            "artifact status is REVIEW",
                        ),
                        (
                            isinstance(body, dict) and bool(body.get("output_id")),
                            "output_id is present",
                        ),
                        (
                            isinstance(body, dict) and bool(body.get("evidence_id")),
                            "evidence_id is present",
                        ),
                        (
                            isinstance(recorded_briefing, dict)
                            and bool(recorded_briefing.get("executive_summary")),
                            "recorded package contains an executive summary",
                        ),
                    ],
                )
            )

            blueprint = blueprint_payload()
            path = f"/api/v1/oaaa/cases/{case_id}/blueprints"
            response = client.post(path, headers=auth(owner_token), json=blueprint)
            body = safe_json(response)
            created = body.get("blueprint", {}) if isinstance(body, dict) else {}
            if response.status_code == 201 and isinstance(created, dict):
                blueprint_id = created.get("blueprint_id")
            results.append(
                classify(
                    check_id="E-012",
                    name="Create OAAA blueprint",
                    method="POST",
                    path=path,
                    expected_status=201,
                    response=response,
                    checks=[
                        (
                            isinstance(created, dict) and created.get("case_id") == case_id,
                            "case scope is derived correctly",
                        ),
                        (
                            isinstance(created, dict)
                            and created.get("organization_id") == org_id,
                            "organization scope is derived correctly",
                        ),
                        (
                            isinstance(created, dict) and created.get("owner_id") == owner_id,
                            "owner is derived from the case",
                        ),
                        (
                            isinstance(created, dict) and created.get("status") == "DRAFT",
                            "initial blueprint status is DRAFT",
                        ),
                        (
                            isinstance(created, dict) and created.get("version") == 1,
                            "initial blueprint version is 1",
                        ),
                        (
                            isinstance(created, dict)
                            and bool(created.get("safety_fingerprint")),
                            "safety fingerprint is present",
                        ),
                        (
                            isinstance(body, dict)
                            and body.get("control_plane_persistence")
                            == "in-memory-development",
                            "temporary OAAA persistence is declared",
                        ),
                    ],
                )
            )

            if blueprint_id is None:
                for check_id, name, method, endpoint_path, expected_status in [
                    (
                        "E-013",
                        "Read latest OAAA blueprint",
                        "GET",
                        "/api/v1/oaaa/blueprints/{blueprint_id}",
                        200,
                    ),
                    (
                        "E-014",
                        "Read OAAA blueprint versions",
                        "GET",
                        "/api/v1/oaaa/blueprints/{blueprint_id}/versions",
                        200,
                    ),
                    (
                        "E-015",
                        "Revise OAAA blueprint",
                        "POST",
                        "/api/v1/oaaa/blueprints/{blueprint_id}/revisions",
                        201,
                    ),
                    (
                        "E-016",
                        "Submit OAAA blueprint",
                        "POST",
                        "/api/v1/oaaa/blueprints/{blueprint_id}/submit",
                        200,
                    ),
                ]:
                    results.append(
                        doubtful(
                            check_id=check_id,
                            name=name,
                            method=method,
                            path=endpoint_path,
                            expected_status=expected_status,
                            reason="Prerequisite E-012 did not produce a usable blueprint_id",
                        )
                    )
            else:
                path = f"/api/v1/oaaa/blueprints/{blueprint_id}"
                response = client.get(path, headers=auth(owner_token))
                body = safe_json(response)
                latest = body.get("blueprint", {}) if isinstance(body, dict) else {}
                results.append(
                    classify(
                        check_id="E-013",
                        name="Read latest OAAA blueprint",
                        method="GET",
                        path=path,
                        expected_status=200,
                        response=response,
                        checks=[
                            (
                                isinstance(latest, dict)
                                and latest.get("blueprint_id") == blueprint_id,
                                "blueprint_id matches",
                            ),
                            (
                                isinstance(latest, dict) and latest.get("version") == 1,
                                "latest version is initially 1",
                            ),
                            (
                                isinstance(latest, dict) and latest.get("status") == "DRAFT",
                                "latest status is DRAFT",
                            ),
                        ],
                    )
                )

                path = f"/api/v1/oaaa/blueprints/{blueprint_id}/versions"
                response = client.get(path, headers=auth(auditor_token))
                body = safe_json(response)
                versions = body.get("versions", []) if isinstance(body, dict) else []
                results.append(
                    classify(
                        check_id="E-014",
                        name="Read OAAA blueprint versions",
                        method="GET",
                        path=path,
                        expected_status=200,
                        response=response,
                        checks=[
                            (
                                isinstance(body, dict)
                                and body.get("blueprint_id") == blueprint_id,
                                "history blueprint_id matches",
                            ),
                            (
                                isinstance(versions, list) and len(versions) == 1,
                                "history initially contains exactly one version",
                            ),
                            (
                                isinstance(versions, list)
                                and bool(versions)
                                and versions[0].get("version") == 1,
                                "history contains version 1",
                            ),
                        ],
                    )
                )

                revision = blueprint_payload()
                revision["objective"] = (
                    "Add scenario comparison while remaining advisory and human-reviewed"
                )
                revision["change_summary"] = "Add bounded scenario comparison"
                path = f"/api/v1/oaaa/blueprints/{blueprint_id}/revisions"
                response = client.post(
                    path,
                    headers=auth(reviewer_token),
                    json=revision,
                )
                body = safe_json(response)
                revised = body.get("blueprint", {}) if isinstance(body, dict) else {}
                results.append(
                    classify(
                        check_id="E-015",
                        name="Revise OAAA blueprint",
                        method="POST",
                        path=path,
                        expected_status=201,
                        response=response,
                        checks=[
                            (
                                isinstance(revised, dict) and revised.get("version") == 2,
                                "revision increments version to 2",
                            ),
                            (
                                isinstance(revised, dict)
                                and revised.get("material_change") is True,
                                "material change is detected",
                            ),
                            (
                                isinstance(revised, dict)
                                and revised.get("parent_version_id") == created.get("id"),
                                "parent_version_id points to version 1",
                            ),
                            (
                                isinstance(revised, dict)
                                and bool(revised.get("safety_fingerprint")),
                                "revised safety fingerprint is present",
                            ),
                        ],
                    )
                )

                path = f"/api/v1/oaaa/blueprints/{blueprint_id}/submit"
                response = client.post(
                    path,
                    headers=auth(owner_token),
                    json={"reason": "Ready for independent OAAA review"},
                )
                body = safe_json(response)
                submitted = body.get("blueprint", {}) if isinstance(body, dict) else {}
                results.append(
                    classify(
                        check_id="E-016",
                        name="Submit OAAA blueprint",
                        method="POST",
                        path=path,
                        expected_status=200,
                        response=response,
                        checks=[
                            (
                                isinstance(submitted, dict)
                                and submitted.get("status") == "IN_REVIEW",
                                "submitted blueprint status is IN_REVIEW",
                            ),
                            (
                                isinstance(submitted, dict)
                                and submitted.get("version") == 3,
                                "submission creates version 3",
                            ),
                            (
                                isinstance(submitted, dict)
                                and submitted.get("blueprint_id") == blueprint_id,
                                "blueprint identity is preserved",
                            ),
                        ],
                    )
                )

    write_reports(results, output_dir)
    verified = sum(result.classification == "FUNCIONA VERIFICADO" for result in results)
    failed = sum(result.classification == "FALLA" for result in results)
    doubtful_count = sum(result.classification == "DUDOSO" for result in results)
    print(
        f"Remaining endpoint verification: verified={verified}, "
        f"failed={failed}, doubtful={doubtful_count}"
    )
    return 0 if verified == 8 and failed == 0 and doubtful_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

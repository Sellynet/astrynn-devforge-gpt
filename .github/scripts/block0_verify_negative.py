from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

import httpx

from block0_verify_remaining import (
    CheckResult,
    atlas_payload,
    auth,
    blueprint_payload,
    classify,
    clearance_payload,
    doubtful,
    safe_json,
)


CheckBuilder = Callable[[httpx.Response, Any], list[tuple[bool, str]]]


def detail_contains(body: Any, *needles: str) -> bool:
    if not isinstance(body, dict):
        return False
    detail = str(body.get("detail", "")).lower()
    return all(needle.lower() in detail for needle in needles)


def write_reports(results: list[CheckResult], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "block0-negative-results.json").write_text(
        json.dumps([asdict(result) for result in results], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    verified = sum(result.classification == "FUNCIONA VERIFICADO" for result in results)
    failed = sum(result.classification == "FALLA" for result in results)
    doubtful_count = sum(result.classification == "DUDOSO" for result in results)

    lines = [
        "# Block 0 · Deliberate Negative Verification",
        "",
        f"- FUNCIONA VERIFICADO: **{verified}**",
        f"- FALLA: **{failed}**",
        f"- DUDOSO: **{doubtful_count}**",
        "",
        (
            "A negative check is verified when the system rejects or contains the "
            "attempted action with the expected status and semantics."
        ),
        "",
        "| ID | Attempt | Expected | Observed | Classification |",
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

    (output_dir / "block0-negative-results.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output-dir", default="verification-artifacts")
    args = parser.parse_args()

    org_a = os.environ["ORG_A"]
    org_b = os.environ["ORG_B"]
    owner_a_id = os.environ["OWNER_A_ID"]
    owner_a = os.environ["OWNER_A_TOKEN"]
    owner_a2 = os.environ["OWNER_A2_TOKEN"]
    reviewer_a = os.environ["REVIEWER_A_TOKEN"]
    viewer_a = os.environ["VIEWER_A_TOKEN"]
    owner_b = os.environ["OWNER_B_TOKEN"]

    results: list[CheckResult] = []

    def run_check(
        *,
        check_id: str,
        name: str,
        method: str,
        path: str,
        expected_status: int,
        request: Callable[[], httpx.Response],
        checks: CheckBuilder,
    ) -> httpx.Response | None:
        try:
            response = request()
            body = safe_json(response)
            results.append(
                classify(
                    check_id=check_id,
                    name=name,
                    method=method,
                    path=path,
                    expected_status=expected_status,
                    response=response,
                    checks=checks(response, body),
                )
            )
            return response
        except Exception as exc:  # noqa: BLE001
            results.append(
                doubtful(
                    check_id=check_id,
                    name=name,
                    method=method,
                    path=path,
                    expected_status=expected_status,
                    reason=f"Request could not be completed: {exc}",
                )
            )
            return None

    def create_case(
        client: httpx.Client,
        *,
        token: str,
        organization_id: str,
        title: str,
    ) -> str:
        response = client.post(
            "/api/v1/cases",
            headers=auth(token),
            json={
                "title": title,
                "description": "Synthetic negative verification case",
                "organization_id": organization_id,
                "sensitivity": "ORANGE",
            },
        )
        response.raise_for_status()
        return str(response.json()["id"])

    with httpx.Client(base_url=args.base_url.rstrip("/"), timeout=20.0) as client:
        run_check(
            check_id="N-001",
            name="Protected endpoint rejects missing token",
            method="GET",
            path="/api/v1/cases",
            expected_status=401,
            request=lambda: client.get("/api/v1/cases"),
            checks=lambda response, body: [
                (response.headers.get("www-authenticate") == "Bearer", "WWW-Authenticate is Bearer"),
                (detail_contains(body, "authentication"), "missing authentication is identified"),
            ],
        )
        run_check(
            check_id="N-002",
            name="Invalid bearer token is rejected",
            method="GET",
            path="/api/v1/cases",
            expected_status=401,
            request=lambda: client.get(
                "/api/v1/cases", headers=auth("deliberately-wrong-token")
            ),
            checks=lambda response, body: [
                (response.headers.get("www-authenticate") == "Bearer", "WWW-Authenticate is Bearer"),
                (detail_contains(body, "invalid", "token"), "invalid token is identified"),
            ],
        )

        spoof_case = {
            "title": "Spoofed identity attempt",
            "description": "Synthetic identity spoof attempt",
            "organization_id": org_a,
            "sensitivity": "ORANGE",
            "actor_id": str(uuid4()),
            "owner_id": str(uuid4()),
        }
        run_check(
            check_id="N-003",
            name="Spoofable actor and owner fields are rejected",
            method="POST",
            path="/api/v1/cases",
            expected_status=422,
            request=lambda: client.post(
                "/api/v1/cases", headers=auth(owner_a), json=spoof_case
            ),
            checks=lambda _response, body: [
                (isinstance(body, dict) and bool(body.get("detail")), "validation detail is returned")
            ],
        )
        run_check(
            check_id="N-004",
            name="Owner cannot create a case for another organization",
            method="POST",
            path="/api/v1/cases",
            expected_status=403,
            request=lambda: client.post(
                "/api/v1/cases",
                headers=auth(owner_a),
                json={
                    "title": "Cross-organization creation attempt",
                    "description": "Synthetic scope violation",
                    "organization_id": org_b,
                    "sensitivity": "ORANGE",
                },
            ),
            checks=lambda _response, body: [
                (detail_contains(body, "organization"), "organization boundary is identified")
            ],
        )

        case_a = create_case(
            client, token=owner_a, organization_id=org_a, title="Negative case A"
        )
        case_b = create_case(
            client, token=owner_b, organization_id=org_b, title="Negative case B"
        )
        run_check(
            check_id="N-005",
            name="Cross-organization case read is denied",
            method="GET",
            path=f"/api/v1/cases/{case_b}",
            expected_status=403,
            request=lambda: client.get(
                f"/api/v1/cases/{case_b}", headers=auth(owner_a)
            ),
            checks=lambda _response, body: [
                (detail_contains(body, "organization"), "organization boundary is identified")
            ],
        )

        prepared = client.post(
            f"/api/v1/cases/{case_a}/transition",
            headers=auth(owner_a),
            json={"target": "IN_REVIEW", "reason": "Prepare self-approval test"},
        )
        prepared.raise_for_status()
        run_check(
            check_id="N-006",
            name="Case owner cannot self-approve",
            method="POST",
            path=f"/api/v1/cases/{case_a}/approvals",
            expected_status=403,
            request=lambda: client.post(
                f"/api/v1/cases/{case_a}/approvals",
                headers=auth(owner_a),
                json={
                    "decision": "APPROVE",
                    "rationale": "Deliberate self-approval attempt",
                    "conditions": [],
                },
            ),
            checks=lambda _response, body: [
                (detail_contains(body, "approve"), "approval restriction is identified")
            ],
        )

        activation_case = create_case(
            client, token=owner_a, organization_id=org_a, title="Owner activation case"
        )
        run_check(
            check_id="N-007",
            name="Case owner cannot activate a case",
            method="POST",
            path=f"/api/v1/cases/{activation_case}/transition",
            expected_status=403,
            request=lambda: client.post(
                f"/api/v1/cases/{activation_case}/transition",
                headers=auth(owner_a),
                json={"target": "ACTIVE", "reason": "Exceed owner authority"},
            ),
            checks=lambda _response, body: [
                (detail_contains(body, "owner"), "owner authority limit is identified")
            ],
        )

        invalid_case = create_case(
            client, token=owner_a, organization_id=org_a, title="Invalid transition case"
        )
        run_check(
            check_id="N-008",
            name="Invalid DRAFT to ACTIVE transition is rejected",
            method="POST",
            path=f"/api/v1/cases/{invalid_case}/transition",
            expected_status=409,
            request=lambda: client.post(
                f"/api/v1/cases/{invalid_case}/transition",
                headers=auth(reviewer_a),
                json={"target": "ACTIVE", "reason": "Skip governed review"},
            ),
            checks=lambda _response, body: [
                (detail_contains(body, "transition"), "invalid transition is identified")
            ],
        )

        aegis_case = create_case(
            client, token=owner_a, organization_id=org_a, title="Aegis negative case"
        )
        run_check(
            check_id="N-009",
            name="Owner cannot record final Aegis Clearance",
            method="POST",
            path=f"/api/v1/aegis/cases/{aegis_case}/clearance/record",
            expected_status=403,
            request=lambda: client.post(
                f"/api/v1/aegis/cases/{aegis_case}/clearance/record",
                headers=auth(owner_a),
                json=clearance_payload(),
            ),
            checks=lambda _response, body: [
                (isinstance(body, dict) and bool(body.get("detail")), "authorization detail is returned")
            ],
        )

        bad_score = clearance_payload()
        bad_score["scores"]["data"] = 6
        run_check(
            check_id="N-010",
            name="Aegis score outside 0 to 5 is rejected",
            method="POST",
            path=f"/api/v1/aegis/cases/{aegis_case}/clearance/evaluate",
            expected_status=422,
            request=lambda: client.post(
                f"/api/v1/aegis/cases/{aegis_case}/clearance/evaluate",
                headers=auth(owner_a),
                json=bad_score,
            ),
            checks=lambda _response, body: [
                (isinstance(body, dict) and bool(body.get("detail")), "validation detail is returned")
            ],
        )

        specialist = clearance_payload()
        specialist["specialist_triggers"] = ["health"]
        run_check(
            check_id="N-011",
            name="Specialist trigger overrides low numeric score",
            method="POST",
            path=f"/api/v1/aegis/cases/{aegis_case}/clearance/evaluate",
            expected_status=200,
            request=lambda: client.post(
                f"/api/v1/aegis/cases/{aegis_case}/clearance/evaluate",
                headers=auth(owner_a),
                json=specialist,
            ),
            checks=lambda _response, body: [
                (
                    isinstance(body, dict)
                    and body.get("result", {}).get("decision")
                    == "REQUIERE_REVISION_ESPECIALIZADA",
                    "decision is REQUIERE_REVISION_ESPECIALIZADA",
                )
            ],
        )

        blocker = clearance_payload()
        blocker["critical_blockers"] = ["No kill switch"]
        run_check(
            check_id="N-012",
            name="Critical blocker prevents APTO",
            method="POST",
            path=f"/api/v1/aegis/cases/{aegis_case}/clearance/evaluate",
            expected_status=200,
            request=lambda: client.post(
                f"/api/v1/aegis/cases/{aegis_case}/clearance/evaluate",
                headers=auth(owner_a),
                json=blocker,
            ),
            checks=lambda _response, body: [
                (
                    isinstance(body, dict)
                    and body.get("result", {}).get("decision") == "NO_APTO_TODAVIA",
                    "decision is NO_APTO_TODAVIA",
                )
            ],
        )
        run_check(
            check_id="N-013",
            name="Viewer cannot evaluate Aegis Clearance",
            method="POST",
            path=f"/api/v1/aegis/cases/{aegis_case}/clearance/evaluate",
            expected_status=403,
            request=lambda: client.post(
                f"/api/v1/aegis/cases/{aegis_case}/clearance/evaluate",
                headers=auth(viewer_a),
                json=clearance_payload(),
            ),
            checks=lambda _response, body: [
                (detail_contains(body, "permission"), "missing permission is identified")
            ],
        )

        atlas_case = create_case(
            client, token=owner_a, organization_id=org_a, title="Atlas negative case"
        )
        run_check(
            check_id="N-014",
            name="Owner cannot record final Atlas briefing",
            method="POST",
            path=f"/api/v1/atlas/cases/{atlas_case}/briefing/record",
            expected_status=403,
            request=lambda: client.post(
                f"/api/v1/atlas/cases/{atlas_case}/briefing/record",
                headers=auth(owner_a),
                json=atlas_payload(),
            ),
            checks=lambda _response, body: [
                (isinstance(body, dict) and bool(body.get("detail")), "authorization detail is returned")
            ],
        )

        broken_atlas = atlas_payload()
        broken_atlas["signals"][0]["source_ids"] = [str(uuid4())]
        run_check(
            check_id="N-015",
            name="Atlas rejects broken source references",
            method="POST",
            path=f"/api/v1/atlas/cases/{atlas_case}/briefing/build",
            expected_status=422,
            request=lambda: client.post(
                f"/api/v1/atlas/cases/{atlas_case}/briefing/build",
                headers=auth(owner_a),
                json=broken_atlas,
            ),
            checks=lambda _response, body: [
                (detail_contains(body, "unknown", "sources"), "unknown sources are identified")
            ],
        )

        oaaa_case = create_case(
            client, token=owner_a, organization_id=org_a, title="OAAA negative case"
        )
        spoof_blueprint = blueprint_payload()
        spoof_blueprint.update(
            {"actor_id": str(uuid4()), "owner_id": str(uuid4()), "organization_id": org_b}
        )
        run_check(
            check_id="N-016",
            name="OAAA rejects spoofable identity fields",
            method="POST",
            path=f"/api/v1/oaaa/cases/{oaaa_case}/blueprints",
            expected_status=422,
            request=lambda: client.post(
                f"/api/v1/oaaa/cases/{oaaa_case}/blueprints",
                headers=auth(owner_a),
                json=spoof_blueprint,
            ),
            checks=lambda _response, body: [
                (isinstance(body, dict) and bool(body.get("detail")), "validation detail is returned")
            ],
        )
        run_check(
            check_id="N-017",
            name="Second owner cannot design for another owner case",
            method="POST",
            path=f"/api/v1/oaaa/cases/{oaaa_case}/blueprints",
            expected_status=403,
            request=lambda: client.post(
                f"/api/v1/oaaa/cases/{oaaa_case}/blueprints",
                headers=auth(owner_a2),
                json=blueprint_payload(),
            ),
            checks=lambda _response, body: [
                (detail_contains(body, "own", "cases"), "owner-level case boundary is identified")
            ],
        )

        wildcard = blueprint_payload()
        wildcard["tools"][0]["allowed_operations"] = ["*"]
        run_check(
            check_id="N-018",
            name="OAAA rejects wildcard tool permissions",
            method="POST",
            path=f"/api/v1/oaaa/cases/{oaaa_case}/blueprints",
            expected_status=422,
            request=lambda: client.post(
                f"/api/v1/oaaa/cases/{oaaa_case}/blueprints",
                headers=auth(owner_a),
                json=wildcard,
            ),
            checks=lambda _response, body: [
                (detail_contains(body, "wildcard"), "wildcard prohibition is identified")
            ],
        )

        incomplete_aria = blueprint_payload()
        incomplete_aria["aria_test_plan"] = incomplete_aria["aria_test_plan"][:-1]
        run_check(
            check_id="N-019",
            name="OAAA rejects incomplete mandatory ARIA families",
            method="POST",
            path=f"/api/v1/oaaa/cases/{oaaa_case}/blueprints",
            expected_status=422,
            request=lambda: client.post(
                f"/api/v1/oaaa/cases/{oaaa_case}/blueprints",
                headers=auth(owner_a),
                json=incomplete_aria,
            ),
            checks=lambda _response, body: [
                (detail_contains(body, "incident_trigger"), "missing INCIDENT_TRIGGER is identified")
            ],
        )

        created = client.post(
            f"/api/v1/oaaa/cases/{oaaa_case}/blueprints",
            headers=auth(owner_a),
            json=blueprint_payload(),
        )
        created.raise_for_status()
        blueprint = created.json()["blueprint"]
        blueprint_id = str(blueprint["blueprint_id"])
        if str(blueprint.get("owner_id")) != owner_a_id:
            raise RuntimeError("Prepared blueprint owner does not match OWNER_A_ID")

        first_submit = client.post(
            f"/api/v1/oaaa/blueprints/{blueprint_id}/submit",
            headers=auth(owner_a),
            json={"reason": "Ready for duplicate submission test"},
        )
        first_submit.raise_for_status()
        run_check(
            check_id="N-020",
            name="Duplicate OAAA submission is rejected",
            method="POST",
            path=f"/api/v1/oaaa/blueprints/{blueprint_id}/submit",
            expected_status=409,
            request=lambda: client.post(
                f"/api/v1/oaaa/blueprints/{blueprint_id}/submit",
                headers=auth(owner_a),
                json={"reason": "Deliberate duplicate submission"},
            ),
            checks=lambda _response, body: [
                (isinstance(body, dict) and bool(body.get("detail")), "transition detail is returned")
            ],
        )
        run_check(
            check_id="N-021",
            name="OAAA activation endpoint is not exposed",
            method="POST",
            path=f"/api/v1/oaaa/blueprints/{blueprint_id}/activate",
            expected_status=404,
            request=lambda: client.post(
                f"/api/v1/oaaa/blueprints/{blueprint_id}/activate",
                headers=auth(reviewer_a),
                json={},
            ),
            checks=lambda _response, body: [
                (detail_contains(body, "not found"), "route is absent and returns Not Found")
            ],
        )
        run_check(
            check_id="N-022",
            name="Cross-organization blueprint read is denied",
            method="GET",
            path=f"/api/v1/oaaa/blueprints/{blueprint_id}",
            expected_status=403,
            request=lambda: client.get(
                f"/api/v1/oaaa/blueprints/{blueprint_id}", headers=auth(owner_b)
            ),
            checks=lambda _response, body: [
                (detail_contains(body, "organization"), "organization boundary is identified")
            ],
        )

    write_reports(results, Path(args.output_dir))
    verified = sum(result.classification == "FUNCIONA VERIFICADO" for result in results)
    failed = sum(result.classification == "FALLA" for result in results)
    doubtful_count = sum(result.classification == "DUDOSO" for result in results)
    print(
        f"Negative verification complete: {verified} verified, "
        f"{failed} failed, {doubtful_count} doubtful"
    )
    for result in results:
        print(f"{result.id}: {result.classification} · {result.name}")
    return 0 if verified == 22 and not failed and not doubtful_count else 1


if __name__ == "__main__":
    sys.exit(main())

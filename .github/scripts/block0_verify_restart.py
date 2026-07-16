from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable
from uuid import UUID

import httpx

from astrynn_devforge.persistence import SQLAlchemyKernelRepository
from block0_verify_remaining import atlas_payload, blueprint_payload, clearance_payload


@dataclass
class CheckResult:
    id: str
    name: str
    expected: str
    observed: str
    classification: str
    checks: list[str]
    failures: list[str]
    evidence: Any


def safe_json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return response.text


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def classified(
    *,
    check_id: str,
    name: str,
    expected: str,
    observed: str,
    checks: list[tuple[bool, str]],
    evidence: Any,
) -> CheckResult:
    failures = [message for passed, message in checks if not passed]
    return CheckResult(
        id=check_id,
        name=name,
        expected=expected,
        observed=observed,
        classification="FUNCIONA VERIFICADO" if not failures else "FALLA",
        checks=[message for passed, message in checks if passed],
        failures=failures,
        evidence=evidence,
    )


def request_result(
    *,
    check_id: str,
    name: str,
    expected_status: int,
    response: httpx.Response,
    semantic_checks: Callable[[Any], list[tuple[bool, str]]],
) -> CheckResult:
    body = safe_json(response)
    checks = [(response.status_code == expected_status, f"HTTP status is {expected_status}")]
    checks.extend(semantic_checks(body))
    return classified(
        check_id=check_id,
        name=name,
        expected=f"HTTP {expected_status} and required semantics",
        observed=f"HTTP {response.status_code}",
        checks=checks,
        evidence=body,
    )


def assert_results(results: list[CheckResult]) -> None:
    failed = [result for result in results if result.classification != "FUNCIONA VERIFICADO"]
    for result in results:
        print(f"{result.id}: {result.classification} - {result.name}")
        for failure in result.failures:
            print(f"  FAILURE: {failure}")
    if failed:
        raise SystemExit(1)


def serialize_results(results: list[CheckResult]) -> list[dict[str, Any]]:
    return [asdict(result) for result in results]


def repository_snapshot(database_url: str, case_id: str) -> dict[str, Any]:
    repository = SQLAlchemyKernelRepository(database_url, create_schema=False)
    try:
        case_uuid = UUID(case_id)
        case = repository.get_case(case_uuid)
        approvals = repository.approvals_for_case(case_uuid)
        outputs = repository.outputs_for_case(case_uuid)
        evidence = repository.evidence_for_case(case_uuid)
        return {
            "case": {
                "id": str(case.id),
                "status": case.status.value,
                "version": case.version,
                "event_ids": [str(event.id) for event in case.events],
                "event_types": [event.event_type for event in case.events],
            },
            "approvals": [
                {
                    "id": str(item.id),
                    "approver_id": str(item.approver_id),
                    "decision": item.decision.value,
                    "conditions": list(item.conditions),
                }
                for item in approvals
            ],
            "outputs": [
                {
                    "id": str(item.id),
                    "artifact_type": item.artifact_type,
                    "owner_id": str(item.owner_id),
                    "version": item.version,
                    "status": item.status.value,
                }
                for item in outputs
            ],
            "evidence": [
                {
                    "id": str(item.id),
                    "label": item.label,
                    "uri": item.uri,
                    "sensitivity": item.sensitivity.value,
                }
                for item in evidence
            ],
        }
    finally:
        repository.close()


def sqlite_counts(database_path: Path, case_id: str) -> dict[str, int]:
    queries = {
        "cases": "SELECT COUNT(*) FROM kernel_cases WHERE id = ?",
        "events": "SELECT COUNT(*) FROM kernel_case_events WHERE case_id = ?",
        "approvals": "SELECT COUNT(*) FROM kernel_approvals WHERE case_id = ?",
        "outputs": "SELECT COUNT(*) FROM kernel_outputs WHERE case_id = ?",
        "evidence": "SELECT COUNT(*) FROM kernel_evidence WHERE case_id = ?",
    }
    with sqlite3.connect(database_path) as connection:
        return {
            name: int(connection.execute(query, (case_id,)).fetchone()[0])
            for name, query in queries.items()
        }


def prepare_phase(base_url: str, state_path: Path) -> None:
    org_id = os.environ["ORG_ID"]
    owner_id = os.environ["OWNER_ID"]
    reviewer_id = os.environ["REVIEWER_ID"]
    owner_token = os.environ["OWNER_TOKEN"]
    reviewer_token = os.environ["REVIEWER_TOKEN"]
    database_url = os.environ["ASTRYNN_DATABASE_URL"]

    results: list[CheckResult] = []
    state: dict[str, Any] = {}

    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        health = client.get("/health")
        results.append(
            request_result(
                check_id="P-001",
                name="First Uvicorn process uses SQLite and in-memory OAAA",
                expected_status=200,
                response=health,
                semantic_checks=lambda body: [
                    (
                        isinstance(body, dict) and body.get("persistence") == "sqlalchemy-sqlite",
                        "Kernel persistence is sqlalchemy-sqlite",
                    ),
                    (
                        isinstance(body, dict)
                        and body.get("oaaa_control_plane_persistence")
                        == "in-memory-development",
                        "OAAA control plane is declared in-memory-development",
                    ),
                ],
            )
        )

        created = client.post(
            "/api/v1/cases",
            headers=auth(owner_token),
            json={
                "title": "Synthetic restart persistence case",
                "description": "Verify durable Kernel records across two Uvicorn processes",
                "organization_id": org_id,
                "sensitivity": "ORANGE",
            },
        )
        created_body = safe_json(created)
        results.append(
            request_result(
                check_id="P-002",
                name="Create durable case before restart",
                expected_status=201,
                response=created,
                semantic_checks=lambda body: [
                    (isinstance(body, dict) and bool(body.get("id")), "case id is present"),
                    (
                        isinstance(body, dict) and body.get("owner_id") == owner_id,
                        "owner is derived from token",
                    ),
                    (
                        isinstance(body, dict) and body.get("organization_id") == org_id,
                        "organization is correct",
                    ),
                    (
                        isinstance(body, dict) and body.get("status") == "DRAFT",
                        "initial status is DRAFT",
                    ),
                ],
            )
        )
        if created.status_code != 201 or not isinstance(created_body, dict):
            assert_results(results)
        case_id = str(created_body["id"])

        submitted = client.post(
            f"/api/v1/cases/{case_id}/transition",
            headers=auth(owner_token),
            json={
                "target": "IN_REVIEW",
                "reason": "Prepare restart persistence verification",
            },
        )
        results.append(
            request_result(
                check_id="P-003",
                name="Transition durable case to IN_REVIEW",
                expected_status=200,
                response=submitted,
                semantic_checks=lambda body: [
                    (
                        isinstance(body, dict) and body.get("status") == "IN_REVIEW",
                        "case status is IN_REVIEW",
                    )
                ],
            )
        )

        approval = client.post(
            f"/api/v1/cases/{case_id}/approvals",
            headers=auth(reviewer_token),
            json={
                "decision": "APPROVE_WITH_CONDITIONS",
                "rationale": "Synthetic persistence case with bounded scope",
                "conditions": ["No external or mutating action"],
            },
        )
        approval_body = safe_json(approval)
        results.append(
            request_result(
                check_id="P-004",
                name="Record independent approval before restart",
                expected_status=201,
                response=approval,
                semantic_checks=lambda body: [
                    (
                        isinstance(body, dict) and body.get("approver_id") == reviewer_id,
                        "reviewer identity is preserved",
                    ),
                    (
                        isinstance(body, dict)
                        and body.get("decision") == "APPROVE_WITH_CONDITIONS",
                        "conditional approval is recorded",
                    ),
                ],
            )
        )

        approved = client.post(
            f"/api/v1/cases/{case_id}/transition",
            headers=auth(reviewer_token),
            json={
                "target": "APPROVED",
                "reason": "Independent approval recorded before restart",
            },
        )
        approved_body = safe_json(approved)
        results.append(
            request_result(
                check_id="P-005",
                name="Advance durable case to APPROVED",
                expected_status=200,
                response=approved,
                semantic_checks=lambda body: [
                    (
                        isinstance(body, dict) and body.get("status") == "APPROVED",
                        "case status is APPROVED",
                    )
                ],
            )
        )

        clearance = client.post(
            f"/api/v1/aegis/cases/{case_id}/clearance/record",
            headers=auth(reviewer_token),
            json=clearance_payload(),
        )
        clearance_body = safe_json(clearance)
        results.append(
            request_result(
                check_id="P-006",
                name="Record Aegis output and evidence before restart",
                expected_status=201,
                response=clearance,
                semantic_checks=lambda body: [
                    (
                        isinstance(body, dict) and bool(body.get("output_id")),
                        "Aegis output id is present",
                    ),
                    (
                        isinstance(body, dict) and bool(body.get("evidence_id")),
                        "Aegis evidence id is present",
                    ),
                    (
                        isinstance(body, dict) and body.get("artifact_status") == "REVIEW",
                        "Aegis artifact status is REVIEW",
                    ),
                ],
            )
        )

        atlas = client.post(
            f"/api/v1/atlas/cases/{case_id}/briefing/record",
            headers=auth(reviewer_token),
            json=atlas_payload(),
        )
        atlas_body = safe_json(atlas)
        results.append(
            request_result(
                check_id="P-007",
                name="Record Atlas output and evidence before restart",
                expected_status=201,
                response=atlas,
                semantic_checks=lambda body: [
                    (
                        isinstance(body, dict) and bool(body.get("output_id")),
                        "Atlas output id is present",
                    ),
                    (
                        isinstance(body, dict) and bool(body.get("evidence_id")),
                        "Atlas evidence id is present",
                    ),
                    (
                        isinstance(body, dict) and body.get("artifact_status") == "REVIEW",
                        "Atlas artifact status is REVIEW",
                    ),
                ],
            )
        )

        blueprint = client.post(
            f"/api/v1/oaaa/cases/{case_id}/blueprints",
            headers=auth(owner_token),
            json=blueprint_payload(),
        )
        blueprint_body = safe_json(blueprint)
        blueprint_id = None
        if isinstance(blueprint_body, dict):
            blueprint_id = blueprint_body.get("blueprint", {}).get("blueprint_id")
        results.append(
            request_result(
                check_id="P-008",
                name="Create temporary OAAA blueprint before restart",
                expected_status=201,
                response=blueprint,
                semantic_checks=lambda body: [
                    (
                        isinstance(body, dict)
                        and body.get("blueprint", {}).get("status") == "DRAFT",
                        "blueprint starts in DRAFT",
                    ),
                    (
                        isinstance(body, dict)
                        and body.get("control_plane_persistence") == "in-memory-development",
                        "response declares in-memory-development persistence",
                    ),
                ],
            )
        )
        if not blueprint_id:
            assert_results(results)

        submitted_blueprint = client.post(
            f"/api/v1/oaaa/blueprints/{blueprint_id}/submit",
            headers=auth(owner_token),
            json={"reason": "Persist only until the first process stops"},
        )
        submitted_blueprint_body = safe_json(submitted_blueprint)
        results.append(
            request_result(
                check_id="P-009",
                name="Place temporary OAAA blueprint in review before restart",
                expected_status=200,
                response=submitted_blueprint,
                semantic_checks=lambda body: [
                    (
                        isinstance(body, dict)
                        and body.get("blueprint", {}).get("status") == "IN_REVIEW",
                        "blueprint status is IN_REVIEW",
                    ),
                    (
                        isinstance(body, dict)
                        and body.get("blueprint", {}).get("version") == 2,
                        "blueprint version is 2",
                    ),
                ],
            )
        )

        final_case = client.get(f"/api/v1/cases/{case_id}", headers=auth(owner_token))
        final_case_body = safe_json(final_case)
        results.append(
            request_result(
                check_id="P-010",
                name="Capture final pre-restart case state",
                expected_status=200,
                response=final_case,
                semantic_checks=lambda body: [
                    (
                        isinstance(body, dict) and body.get("status") == "APPROVED",
                        "case remains APPROVED",
                    ),
                    (
                        isinstance(body, dict) and len(body.get("events", [])) >= 3,
                        "case has a traceable event history",
                    ),
                ],
            )
        )

    assert_results(results)

    snapshot = repository_snapshot(database_url, case_id)
    state = {
        "case_id": case_id,
        "owner_id": owner_id,
        "reviewer_id": reviewer_id,
        "approval_id": approval_body["id"],
        "clearance_output_id": clearance_body["output_id"],
        "clearance_evidence_id": clearance_body["evidence_id"],
        "atlas_output_id": atlas_body["output_id"],
        "atlas_evidence_id": atlas_body["evidence_id"],
        "blueprint_id": blueprint_id,
        "blueprint_status": submitted_blueprint_body["blueprint"]["status"],
        "blueprint_version": submitted_blueprint_body["blueprint"]["version"],
        "case_status": approved_body["status"],
        "case_version": approved_body["version"],
        "event_ids": [item["id"] for item in final_case_body["events"]],
        "pre_restart_repository_snapshot": snapshot,
        "prepare_results": serialize_results(results),
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Restart state written to {state_path}")


def verify_phase(base_url: str, state_path: Path, output_dir: Path) -> None:
    owner_token = os.environ["OWNER_TOKEN"]
    database_url = os.environ["ASTRYNN_DATABASE_URL"]
    database_path = Path(os.environ["DATABASE_PATH"])
    state = json.loads(state_path.read_text(encoding="utf-8"))
    case_id = state["case_id"]
    blueprint_id = state["blueprint_id"]

    results = [CheckResult(**item) for item in state["prepare_results"]]
    post_results: list[CheckResult] = []

    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        health = client.get("/health")
        health_body = safe_json(health)
        post_results.append(
            request_result(
                check_id="P-011",
                name="Second Uvicorn process reopens the same SQLite Kernel",
                expected_status=200,
                response=health,
                semantic_checks=lambda body: [
                    (
                        isinstance(body, dict) and body.get("persistence") == "sqlalchemy-sqlite",
                        "Kernel persistence remains sqlalchemy-sqlite",
                    ),
                    (
                        isinstance(body, dict)
                        and body.get("oaaa_control_plane_persistence")
                        == "in-memory-development",
                        "new OAAA control plane is again empty in memory",
                    ),
                ],
            )
        )

        recovered = client.get(f"/api/v1/cases/{case_id}", headers=auth(owner_token))
        recovered_body = safe_json(recovered)
        recovered_event_ids = (
            [item.get("id") for item in recovered_body.get("events", [])]
            if isinstance(recovered_body, dict)
            else []
        )
        post_results.append(
            request_result(
                check_id="P-012",
                name="Case state and event history survive restart",
                expected_status=200,
                response=recovered,
                semantic_checks=lambda body: [
                    (
                        isinstance(body, dict) and body.get("id") == case_id,
                        "same case id is recovered",
                    ),
                    (
                        isinstance(body, dict) and body.get("status") == state["case_status"],
                        "case status matches pre-restart state",
                    ),
                    (
                        isinstance(body, dict) and body.get("version") == state["case_version"],
                        "case version matches pre-restart state",
                    ),
                    (
                        recovered_event_ids == state["event_ids"],
                        "event ids and ordering match pre-restart state",
                    ),
                ],
            )
        )

        listed = client.get("/api/v1/cases", headers=auth(owner_token))
        post_results.append(
            request_result(
                check_id="P-013",
                name="Recovered case remains discoverable through list endpoint",
                expected_status=200,
                response=listed,
                semantic_checks=lambda body: [
                    (
                        isinstance(body, list)
                        and any(item.get("id") == case_id for item in body),
                        "list endpoint contains the recovered case",
                    )
                ],
            )
        )

        lost_blueprint = client.get(
            f"/api/v1/oaaa/blueprints/{blueprint_id}",
            headers=auth(owner_token),
        )
        post_results.append(
            request_result(
                check_id="P-017",
                name="OAAA blueprint loss after restart is explicit and expected",
                expected_status=404,
                response=lost_blueprint,
                semantic_checks=lambda body: [
                    (
                        isinstance(body, dict) and body.get("detail") == "Blueprint not found",
                        "API reports Blueprint not found",
                    ),
                    (
                        isinstance(health_body, dict)
                        and health_body.get("oaaa_control_plane_persistence")
                        == "in-memory-development",
                        "loss is consistent with declared in-memory persistence",
                    ),
                ],
            )
        )

        reevaluated = client.post(
            f"/api/v1/aegis/cases/{case_id}/clearance/evaluate",
            headers=auth(owner_token),
            json=clearance_payload(),
        )
        post_results.append(
            request_result(
                check_id="P-018",
                name="Recovered case remains usable for governed evaluation",
                expected_status=200,
                response=reevaluated,
                semantic_checks=lambda body: [
                    (
                        isinstance(body, dict)
                        and body.get("result", {}).get("decision") == "APTO",
                        "Aegis can evaluate the recovered case",
                    ),
                    (
                        isinstance(body, dict)
                        and body.get("result", {}).get("total_score") == 9,
                        "deterministic total score remains 9",
                    ),
                ],
            )
        )

    snapshot = repository_snapshot(database_url, case_id)
    pre_snapshot = state["pre_restart_repository_snapshot"]
    approval_ids = {item["id"] for item in snapshot["approvals"]}
    output_ids = {item["id"] for item in snapshot["outputs"]}
    evidence_ids = {item["id"] for item in snapshot["evidence"]}
    output_types = {item["artifact_type"] for item in snapshot["outputs"]}
    evidence_labels = {item["label"] for item in snapshot["evidence"]}

    post_results.append(
        classified(
            check_id="P-014",
            name="Approval record survives restart",
            expected="Exact approval id and decision remain queryable",
            observed=f"{len(snapshot['approvals'])} approval record(s)",
            checks=[
                (state["approval_id"] in approval_ids, "exact approval id is recovered"),
                (
                    snapshot["approvals"] == pre_snapshot["approvals"],
                    "approval snapshot matches pre-restart state",
                ),
            ],
            evidence=snapshot["approvals"],
        )
    )

    post_results.append(
        classified(
            check_id="P-015",
            name="Aegis and Atlas outputs survive restart",
            expected="Exact output ids and artifact types remain queryable",
            observed=f"{len(snapshot['outputs'])} output record(s)",
            checks=[
                (
                    {state["clearance_output_id"], state["atlas_output_id"]}
                    <= output_ids,
                    "both exact output ids are recovered",
                ),
                (
                    {"AEGIS_CLEARANCE_REPORT", "ORBYN_ATLAS_BRIEFING"}
                    <= output_types,
                    "Aegis and Atlas artifact types are recovered",
                ),
                (
                    snapshot["outputs"] == pre_snapshot["outputs"],
                    "output snapshot matches pre-restart state",
                ),
            ],
            evidence=snapshot["outputs"],
        )
    )

    post_results.append(
        classified(
            check_id="P-016",
            name="Aegis and Atlas evidence survive restart",
            expected="Exact evidence ids and labels remain queryable",
            observed=f"{len(snapshot['evidence'])} evidence record(s)",
            checks=[
                (
                    {state["clearance_evidence_id"], state["atlas_evidence_id"]}
                    <= evidence_ids,
                    "both exact evidence ids are recovered",
                ),
                (
                    {
                        "Aegis Clearance Proof Receipt",
                        "Orbyn Atlas Briefing Proof Receipt",
                    }
                    <= evidence_labels,
                    "Aegis and Atlas evidence labels are recovered",
                ),
                (
                    snapshot["evidence"] == pre_snapshot["evidence"],
                    "evidence snapshot matches pre-restart state",
                ),
            ],
            evidence=snapshot["evidence"],
        )
    )

    counts = sqlite_counts(database_path, case_id)
    post_results.append(
        classified(
            check_id="P-019",
            name="Durable records exist physically in the SQLite file",
            expected="1 case, matching events, 1 approval, 2 outputs and 2 evidence rows",
            observed=json.dumps(counts, sort_keys=True),
            checks=[
                (database_path.exists(), "SQLite file exists after both processes"),
                (database_path.stat().st_size > 0, "SQLite file is non-empty"),
                (counts["cases"] == 1, "one case row exists"),
                (
                    counts["events"] == len(state["event_ids"]),
                    "event row count matches captured history",
                ),
                (counts["approvals"] == 1, "one approval row exists"),
                (counts["outputs"] == 2, "two output rows exist"),
                (counts["evidence"] == 2, "two evidence rows exist"),
            ],
            evidence={
                "database_path": str(database_path),
                "size_bytes": database_path.stat().st_size,
                "counts": counts,
            },
        )
    )

    results.extend(post_results)
    write_reports(results, output_dir, state)
    assert_results(results)


def write_reports(
    results: list[CheckResult],
    output_dir: Path,
    state: dict[str, Any],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "block0-restart-persistence-results.json"
    json_path.write_text(
        json.dumps(
            {
                "state": state,
                "results": serialize_results(results),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    verified = sum(result.classification == "FUNCIONA VERIFICADO" for result in results)
    failed = sum(result.classification == "FALLA" for result in results)
    doubtful = sum(result.classification == "DUDOSO" for result in results)

    lines = [
        "# Block 0 · Restart Persistence Verification",
        "",
        f"- FUNCIONA VERIFICADO: **{verified}**",
        f"- FALLA: **{failed}**",
        f"- DUDOSO: **{doubtful}**",
        "",
        "Two distinct Uvicorn processes used the same SQLite file.",
        "",
        "| ID | Check | Expected | Observed | Classification |",
        "|---|---|---|---|---|",
    ]
    for result in results:
        lines.append(
            f"| {result.id} | {result.name} | {result.expected} | "
            f"{result.observed} | **{result.classification}** |"
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
                "Evidence:",
                "",
                "```json",
                json.dumps(result.evidence, ensure_ascii=False, indent=2),
                "```",
            ]
        )

    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "- Kernel case, event, approval, output and evidence records are durable in SQLite.",
            "- Aegis and Atlas records survive because they are stored through the Kernel repository.",
            "- The OAAA blueprint is intentionally absent after restart because the control plane is",
            "  still declared as `in-memory-development`.",
            "- This does not verify PostgreSQL, Supabase, multi-runner concurrency or production identity.",
        ]
    )

    markdown_path = output_dir / "block0-restart-persistence-results.md"
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("prepare", "verify"), required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--state-file", default="verification-artifacts/restart-state.json")
    parser.add_argument("--output-dir", default="verification-artifacts")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    state_path = Path(args.state_file)
    output_dir = Path(args.output_dir)

    try:
        if args.phase == "prepare":
            prepare_phase(base_url, state_path)
        else:
            verify_phase(base_url, state_path, output_dir)
    except Exception as exc:  # noqa: BLE001
        print(f"Unexpected persistence verifier error: {exc!r}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

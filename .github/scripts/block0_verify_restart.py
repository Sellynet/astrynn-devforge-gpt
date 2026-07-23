from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

import httpx
from block0_verify_remaining import atlas_payload, blueprint_payload, clearance_payload

from astrynn_devforge.persistence import SQLAlchemyKernelRepository


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


def result(
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


def http_result(
    check_id: str,
    name: str,
    expected_status: int,
    response: httpx.Response,
    semantic_checks: Callable[[Any], list[tuple[bool, str]]],
) -> CheckResult:
    body = safe_json(response)
    checks = [(response.status_code == expected_status, f"HTTP status is {expected_status}")]
    checks.extend(semantic_checks(body))
    return result(
        check_id,
        name,
        f"HTTP {expected_status} with required semantics",
        f"HTTP {response.status_code}",
        checks,
        body,
    )


def enforce(results: list[CheckResult]) -> None:
    for item in results:
        print(f"{item.id}: {item.classification} - {item.name}")
        for failure in item.failures:
            print(f"  FAILURE: {failure}")
    if any(item.classification != "FUNCIONA VERIFICADO" for item in results):
        raise SystemExit(1)


def repository_snapshot(database_url: str, case_id: str) -> dict[str, Any]:
    repository = SQLAlchemyKernelRepository(database_url, create_schema=False)
    try:
        case_uuid = UUID(case_id)
        case = repository.get_case(case_uuid)
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
                for item in repository.approvals_for_case(case_uuid)
            ],
            "outputs": [
                {
                    "id": str(item.id),
                    "artifact_type": item.artifact_type,
                    "owner_id": str(item.owner_id),
                    "version": item.version,
                    "status": item.status.value,
                }
                for item in repository.outputs_for_case(case_uuid)
            ],
            "evidence": [
                {
                    "id": str(item.id),
                    "label": item.label,
                    "uri": item.uri,
                    "sensitivity": item.sensitivity.value,
                }
                for item in repository.evidence_for_case(case_uuid)
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


def prepare(base_url: str, state_path: Path) -> None:
    org_id = os.environ["ORG_ID"]
    owner_id = os.environ["OWNER_ID"]
    reviewer_id = os.environ["REVIEWER_ID"]
    owner_token = os.environ["OWNER_TOKEN"]
    reviewer_token = os.environ["REVIEWER_TOKEN"]
    database_url = os.environ["ASTRYNN_DATABASE_URL"]
    checks: list[CheckResult] = []

    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        response = client.get("/health")
        checks.append(
            http_result(
                "P-001",
                "First process uses SQLite with volatile OAAA",
                200,
                response,
                lambda body: [
                    (
                        isinstance(body, dict) and body.get("persistence") == "sqlalchemy-sqlite",
                        "Kernel persistence is sqlalchemy-sqlite",
                    ),
                    (
                        isinstance(body, dict)
                        and body.get("oaaa_control_plane_persistence")
                        == "in-memory-development",
                        "OAAA is declared in-memory-development",
                    ),
                ],
            )
        )

        response = client.post(
            "/api/v1/cases",
            headers=auth(owner_token),
            json={
                "title": "Synthetic restart persistence case",
                "description": "Durability verification across two Uvicorn processes",
                "organization_id": org_id,
                "sensitivity": "ORANGE",
            },
        )
        body = safe_json(response)
        checks.append(
            http_result(
                "P-002",
                "Create case before restart",
                201,
                response,
                lambda item: [
                    (isinstance(item, dict) and bool(item.get("id")), "case id is present"),
                    (
                        isinstance(item, dict) and item.get("owner_id") == owner_id,
                        "owner is derived from token",
                    ),
                ],
            )
        )
        if response.status_code != 201 or not isinstance(body, dict):
            enforce(checks)
        case_id = str(body["id"])

        response = client.post(
            f"/api/v1/cases/{case_id}/transition",
            headers=auth(owner_token),
            json={"target": "IN_REVIEW", "reason": "Prepare restart verification"},
        )
        checks.append(
            http_result(
                "P-003",
                "Transition case to IN_REVIEW",
                200,
                response,
                lambda item: [
                    (
                        isinstance(item, dict) and item.get("status") == "IN_REVIEW",
                        "case status is IN_REVIEW",
                    )
                ],
            )
        )

        response = client.post(
            f"/api/v1/cases/{case_id}/approvals",
            headers=auth(reviewer_token),
            json={
                "decision": "APPROVE_WITH_CONDITIONS",
                "rationale": "Bounded synthetic persistence case",
                "conditions": ["No external or mutating action"],
            },
        )
        approval = safe_json(response)
        checks.append(
            http_result(
                "P-004",
                "Record independent approval",
                201,
                response,
                lambda item: [
                    (
                        isinstance(item, dict) and item.get("approver_id") == reviewer_id,
                        "reviewer identity is preserved",
                    )
                ],
            )
        )

        response = client.post(
            f"/api/v1/cases/{case_id}/transition",
            headers=auth(reviewer_token),
            json={"target": "APPROVED", "reason": "Approval recorded"},
        )
        checks.append(
            http_result(
                "P-005",
                "Advance case to APPROVED",
                200,
                response,
                lambda item: [
                    (
                        isinstance(item, dict) and item.get("status") == "APPROVED",
                        "case status is APPROVED",
                    )
                ],
            )
        )

        response = client.post(
            f"/api/v1/aegis/cases/{case_id}/clearance/record",
            headers=auth(reviewer_token),
            json=clearance_payload(),
        )
        clearance = safe_json(response)
        checks.append(
            http_result(
                "P-006",
                "Record Aegis output and evidence",
                201,
                response,
                lambda item: [
                    (isinstance(item, dict) and bool(item.get("output_id")), "output id exists"),
                    (
                        isinstance(item, dict) and bool(item.get("evidence_id")),
                        "evidence id exists",
                    ),
                ],
            )
        )

        response = client.post(
            f"/api/v1/atlas/cases/{case_id}/briefing/record",
            headers=auth(reviewer_token),
            json=atlas_payload(),
        )
        atlas = safe_json(response)
        checks.append(
            http_result(
                "P-007",
                "Record Atlas output and evidence",
                201,
                response,
                lambda item: [
                    (isinstance(item, dict) and bool(item.get("output_id")), "output id exists"),
                    (
                        isinstance(item, dict) and bool(item.get("evidence_id")),
                        "evidence id exists",
                    ),
                ],
            )
        )

        response = client.post(
            f"/api/v1/oaaa/cases/{case_id}/blueprints",
            headers=auth(owner_token),
            json=blueprint_payload(),
        )
        blueprint = safe_json(response)
        blueprint_id = (
            blueprint.get("blueprint", {}).get("blueprint_id")
            if isinstance(blueprint, dict)
            else None
        )
        checks.append(
            http_result(
                "P-008",
                "Create OAAA blueprint before restart",
                201,
                response,
                lambda item: [
                    (
                        isinstance(item, dict)
                        and item.get("blueprint", {}).get("status") == "DRAFT",
                        "blueprint starts in DRAFT",
                    )
                ],
            )
        )
        if not blueprint_id:
            enforce(checks)

        response = client.post(
            f"/api/v1/oaaa/blueprints/{blueprint_id}/submit",
            headers=auth(owner_token),
            json={"reason": "Verify volatile control-plane state"},
        )
        submitted_blueprint = safe_json(response)
        checks.append(
            http_result(
                "P-009",
                "Submit OAAA blueprint before restart",
                200,
                response,
                lambda item: [
                    (
                        isinstance(item, dict)
                        and item.get("blueprint", {}).get("status") == "IN_REVIEW",
                        "blueprint status is IN_REVIEW",
                    ),
                    (
                        isinstance(item, dict)
                        and item.get("blueprint", {}).get("version") == 2,
                        "blueprint version is 2",
                    ),
                ],
            )
        )

        response = client.get(f"/api/v1/cases/{case_id}", headers=auth(owner_token))
        public_case = safe_json(response)
        checks.append(
            http_result(
                "P-010",
                "Capture public case state before restart",
                200,
                response,
                lambda item: [
                    (
                        isinstance(item, dict) and item.get("status") == "APPROVED",
                        "case remains APPROVED",
                    ),
                    (
                        isinstance(item, dict) and len(item.get("events", [])) >= 3,
                        "event history is present",
                    ),
                ],
            )
        )

    enforce(checks)
    snapshot = repository_snapshot(database_url, case_id)
    state = {
        "case_id": case_id,
        "approval_id": approval["id"],
        "clearance_output_id": clearance["output_id"],
        "clearance_evidence_id": clearance["evidence_id"],
        "atlas_output_id": atlas["output_id"],
        "atlas_evidence_id": atlas["evidence_id"],
        "blueprint_id": blueprint_id,
        "blueprint_status": submitted_blueprint["blueprint"]["status"],
        "blueprint_version": submitted_blueprint["blueprint"]["version"],
        "public_status": public_case["status"],
        "public_event_types": [item["event_type"] for item in public_case["events"]],
        "pre_snapshot": snapshot,
        "prepare_results": [asdict(item) for item in checks],
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Restart state written to {state_path}")


def verify(base_url: str, state_path: Path, output_dir: Path) -> None:
    owner_token = os.environ["OWNER_TOKEN"]
    database_url = os.environ["ASTRYNN_DATABASE_URL"]
    database_path = Path(os.environ["DATABASE_PATH"])
    state = json.loads(state_path.read_text(encoding="utf-8"))
    case_id = state["case_id"]
    pre = state["pre_snapshot"]
    checks = [CheckResult(**item) for item in state["prepare_results"]]

    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        response = client.get("/health")
        health = safe_json(response)
        checks.append(
            http_result(
                "P-011",
                "Second process reopens SQLite with fresh OAAA memory",
                200,
                response,
                lambda item: [
                    (
                        isinstance(item, dict) and item.get("persistence") == "sqlalchemy-sqlite",
                        "Kernel persistence remains sqlalchemy-sqlite",
                    ),
                    (
                        isinstance(item, dict)
                        and item.get("oaaa_control_plane_persistence")
                        == "in-memory-development",
                        "OAAA is still declared in-memory-development",
                    ),
                ],
            )
        )

        response = client.get(f"/api/v1/cases/{case_id}", headers=auth(owner_token))
        recovered = safe_json(response)
        recovered_types = (
            [item.get("event_type") for item in recovered.get("events", [])]
            if isinstance(recovered, dict)
            else []
        )
        checks.append(
            http_result(
                "P-012",
                "Public case state survives restart",
                200,
                response,
                lambda item: [
                    (isinstance(item, dict) and item.get("id") == case_id, "same case id returns"),
                    (
                        isinstance(item, dict) and item.get("status") == state["public_status"],
                        "case status matches pre-restart state",
                    ),
                    (
                        recovered_types == state["public_event_types"],
                        "event types and ordering match",
                    ),
                ],
            )
        )

        response = client.get("/api/v1/cases", headers=auth(owner_token))
        checks.append(
            http_result(
                "P-013",
                "Recovered case remains listable",
                200,
                response,
                lambda item: [
                    (
                        isinstance(item, list) and any(row.get("id") == case_id for row in item),
                        "list contains the recovered case",
                    )
                ],
            )
        )

        response = client.get(
            f"/api/v1/oaaa/blueprints/{state['blueprint_id']}",
            headers=auth(owner_token),
        )
        checks.append(
            http_result(
                "P-018",
                "OAAA operational blueprint is lost as declared",
                404,
                response,
                lambda item: [
                    (
                        isinstance(item, dict) and item.get("detail") == "Blueprint not found",
                        "API reports Blueprint not found",
                    ),
                    (
                        isinstance(health, dict)
                        and health.get("oaaa_control_plane_persistence")
                        == "in-memory-development",
                        "loss is consistent with the declared control plane",
                    ),
                ],
            )
        )

        response = client.post(
            f"/api/v1/aegis/cases/{case_id}/clearance/evaluate",
            headers=auth(owner_token),
            json=clearance_payload(),
        )
        checks.append(
            http_result(
                "P-019",
                "Recovered case remains usable by Aegis",
                200,
                response,
                lambda item: [
                    (
                        isinstance(item, dict)
                        and item.get("result", {}).get("decision") == "APTO",
                        "decision remains APTO",
                    ),
                    (
                        isinstance(item, dict)
                        and item.get("result", {}).get("total_score") == 9,
                        "total score remains 9",
                    ),
                ],
            )
        )

    post = repository_snapshot(database_url, case_id)
    checks.append(
        result(
            "P-014",
            "Exact Kernel case version and event IDs survive",
            "case snapshot equals pre-restart snapshot",
            f"version {post['case']['version']}",
            [(post["case"] == pre["case"], "case snapshot is identical")],
            post["case"],
        )
    )
    checks.append(
        result(
            "P-015",
            "Approval records survive",
            "approval snapshot equals pre-restart snapshot",
            f"{len(post['approvals'])} approval record(s)",
            [
                (post["approvals"] == pre["approvals"], "approval snapshot is identical"),
                (
                    state["approval_id"] in {item["id"] for item in post["approvals"]},
                    "exact approval id is recovered",
                ),
            ],
            post["approvals"],
        )
    )
    checks.append(
        result(
            "P-016",
            "All output artifacts survive, including OAAA audit artifacts",
            "output snapshot equals pre-restart snapshot",
            f"{len(post['outputs'])} output record(s)",
            [
                (post["outputs"] == pre["outputs"], "output snapshot is identical"),
                (
                    {state["clearance_output_id"], state["atlas_output_id"]}
                    <= {item["id"] for item in post["outputs"]},
                    "exact Aegis and Atlas output ids are recovered",
                ),
                (
                    any(
                        item["artifact_type"] == "OAAA_AGENT_BLUEPRINT"
                        for item in post["outputs"]
                    ),
                    "OAAA audit artifacts remain in the durable Kernel",
                ),
            ],
            post["outputs"],
        )
    )
    checks.append(
        result(
            "P-017",
            "All evidence survives, including OAAA audit evidence",
            "evidence snapshot equals pre-restart snapshot",
            f"{len(post['evidence'])} evidence record(s)",
            [
                (post["evidence"] == pre["evidence"], "evidence snapshot is identical"),
                (
                    {state["clearance_evidence_id"], state["atlas_evidence_id"]}
                    <= {item["id"] for item in post["evidence"]},
                    "exact Aegis and Atlas evidence ids are recovered",
                ),
                (
                    any(item["uri"].startswith("oaaa://") for item in post["evidence"]),
                    "OAAA audit evidence remains in the durable Kernel",
                ),
            ],
            post["evidence"],
        )
    )

    counts = sqlite_counts(database_path, case_id)
    expected_counts = {
        "cases": 1,
        "events": len(pre["case"]["event_ids"]),
        "approvals": len(pre["approvals"]),
        "outputs": len(pre["outputs"]),
        "evidence": len(pre["evidence"]),
    }
    checks.append(
        result(
            "P-020",
            "Physical SQLite rows match the pre-restart baseline",
            json.dumps(expected_counts, sort_keys=True),
            json.dumps(counts, sort_keys=True),
            [
                (database_path.exists(), "SQLite file exists"),
                (database_path.stat().st_size > 0, "SQLite file is non-empty"),
                (counts == expected_counts, "all physical row counts match the baseline"),
            ],
            {
                "database_path": str(database_path),
                "size_bytes": database_path.stat().st_size,
                "expected_counts": expected_counts,
                "observed_counts": counts,
            },
        )
    )

    write_reports(checks, output_dir, state)
    enforce(checks)


def write_reports(results: list[CheckResult], output_dir: Path, state: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "block0-restart-persistence-results.json").write_text(
        json.dumps(
            {"state": state, "results": [asdict(item) for item in results]},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    verified = sum(item.classification == "FUNCIONA VERIFICADO" for item in results)
    failed = sum(item.classification == "FALLA" for item in results)
    doubtful = sum(item.classification == "DUDOSO" for item in results)
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
    for item in results:
        lines.append(
            f"| {item.id} | {item.name} | {item.expected} | {item.observed} | "
            f"**{item.classification}** |"
        )
    for item in results:
        lines.extend(
            [
                "",
                f"## {item.id} · {item.name}",
                "",
                f"Classification: **{item.classification}**",
                "",
                "Checks passed:",
                *[f"- {entry}" for entry in item.checks],
            ]
        )
        if item.failures:
            lines.extend(["", "Failures:", *[f"- {entry}" for entry in item.failures]])
        lines.extend(
            [
                "",
                "Evidence:",
                "",
                "```json",
                json.dumps(item.evidence, ensure_ascii=False, indent=2),
                "```",
            ]
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "- Kernel cases, events, approvals, outputs and evidence are durable in SQLite.",
            "- Aegis and Atlas records survive through the SQL-backed Kernel repository.",
            "- OAAA operational state is volatile, but its Kernel audit artifacts survive.",
            "- This does not verify PostgreSQL, Supabase, concurrency or production identity.",
        ]
    )
    (output_dir / "block0-restart-persistence-results.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("prepare", "verify"), required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--state-file", default="verification-artifacts/restart-state.json")
    parser.add_argument("--output-dir", default="verification-artifacts")
    args = parser.parse_args()
    try:
        if args.phase == "prepare":
            prepare(args.base_url.rstrip("/"), Path(args.state_file))
        else:
            verify(
                args.base_url.rstrip("/"),
                Path(args.state_file),
                Path(args.output_dir),
            )
    except Exception as exc:  # noqa: BLE001
        print(f"Unexpected persistence verifier error: {exc!r}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256
import json
from typing import Any
from uuid import UUID, uuid4

from astrynn_devforge.aegis import ClearanceDecision
from astrynn_devforge.kernel import Sensitivity

from .enums import ARIATestFamily, AutonomyLevel, BlueprintStatus, HumanDecision


_FORBIDDEN_ACTION_FRAGMENTS = (
    "approve own",
    "self approve",
    "elevate permission",
    "grant admin",
    "issue credential",
    "create credential",
    "deploy to production",
    "disable logging",
    "delete audit",
    "modify guardrail",
    "bypass approval",
)

_FORBIDDEN_TOOL_FRAGMENTS = (
    "root shell",
    "iam admin",
    "credential issuer",
    "permission admin",
    "deployment admin",
)

_MUTATING_ACTION_FRAGMENTS = (
    "send",
    "write",
    "delete",
    "execute",
    "publish",
    "deploy",
    "update",
    "create",
    "approve",
)

_REQUIRED_ARIA_FAMILIES = {
    ARIATestFamily.PROMPT_INJECTION,
    ARIATestFamily.TOOL_PERMISSION_DRIFT,
    ARIATestFamily.INCIDENT_TRIGGER,
}


def utc_now() -> datetime:
    return datetime.now(UTC)


def _require_text(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


def _require_text_tuple(values: tuple[str, ...], field_name: str) -> None:
    if not values:
        raise ValueError(f"{field_name} requires at least one value")
    for value in values:
        _require_text(value, field_name)


def _normalize(value: str) -> str:
    return " ".join(value.lower().replace("_", " ").replace("-", " ").split())


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True, slots=True)
class ToolPermission:
    name: str
    allowed_operations: tuple[str, ...]
    prohibited_operations: tuple[str, ...] = ()
    requires_human_approval: bool = True

    def __post_init__(self) -> None:
        _require_text(self.name, "Tool name")
        _require_text_tuple(self.allowed_operations, "Allowed tool operations")
        for operation in self.prohibited_operations:
            _require_text(operation, "Prohibited tool operation")
        if any(operation.strip() == "*" for operation in self.allowed_operations):
            raise ValueError("Wildcard tool operations are not allowed")
        normalized_name = _normalize(self.name)
        if any(fragment in normalized_name for fragment in _FORBIDDEN_TOOL_FRAGMENTS):
            raise ValueError(f"Tool {self.name!r} is outside the OAAA v0.1 permission boundary")

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name.strip(),
            "allowed_operations": list(self.allowed_operations),
            "prohibited_operations": list(self.prohibited_operations),
            "requires_human_approval": self.requires_human_approval,
        }


@dataclass(frozen=True, slots=True)
class DataBoundary:
    allowed_categories: tuple[str, ...]
    prohibited_categories: tuple[str, ...]
    retention_rule: str
    deletion_rule: str

    def __post_init__(self) -> None:
        _require_text_tuple(self.allowed_categories, "Allowed data categories")
        _require_text_tuple(self.prohibited_categories, "Prohibited data categories")
        _require_text(self.retention_rule, "Retention rule")
        _require_text(self.deletion_rule, "Deletion rule")
        overlap = {
            _normalize(value) for value in self.allowed_categories
        } & {_normalize(value) for value in self.prohibited_categories}
        if overlap:
            raise ValueError("A data category cannot be both allowed and prohibited")

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed_categories": list(self.allowed_categories),
            "prohibited_categories": list(self.prohibited_categories),
            "retention_rule": self.retention_rule.strip(),
            "deletion_rule": self.deletion_rule.strip(),
        }


@dataclass(frozen=True, slots=True)
class ApprovalPoint:
    trigger: str
    approver_role: str
    action_if_unavailable: str = "STOP"

    def __post_init__(self) -> None:
        _require_text(self.trigger, "Approval trigger")
        _require_text(self.approver_role, "Approver role")
        _require_text(self.action_if_unavailable, "Action if approver is unavailable")

    def to_dict(self) -> dict[str, str]:
        return {
            "trigger": self.trigger.strip(),
            "approver_role": self.approver_role.strip(),
            "action_if_unavailable": self.action_if_unavailable.strip(),
        }


@dataclass(frozen=True, slots=True)
class ARIATestRequirement:
    family: ARIATestFamily
    objective: str
    pass_criteria: str

    def __post_init__(self) -> None:
        _require_text(self.objective, "ARIA test objective")
        _require_text(self.pass_criteria, "ARIA pass criteria")

    def to_dict(self) -> dict[str, str]:
        return {
            "family": self.family.value,
            "objective": self.objective.strip(),
            "pass_criteria": self.pass_criteria.strip(),
        }


@dataclass(frozen=True, slots=True)
class AgentBlueprintVersion:
    blueprint_id: UUID
    case_id: UUID
    organization_id: UUID
    owner_id: UUID
    created_by: UUID
    name: str
    business_need: str
    role: str
    objective: str
    tools: tuple[ToolPermission, ...]
    data_boundary: DataBoundary
    allowed_actions: tuple[str, ...]
    prohibited_actions: tuple[str, ...]
    autonomy_level: AutonomyLevel
    approval_points: tuple[ApprovalPoint, ...]
    logs_required: tuple[str, ...]
    aria_test_plan: tuple[ARIATestRequirement, ...]
    rollback_procedure: str
    disable_procedure: str
    sensitivity: Sensitivity
    version: int
    status: BlueprintStatus
    material_change: bool
    id: UUID = field(default_factory=uuid4)
    vault_artifact_id: UUID | None = None
    parent_version_id: UUID | None = None
    clearance_result_id: UUID | None = None
    clearance_decision: ClearanceDecision | None = None
    clearance_conditions: tuple[str, ...] = ()
    clearance_guardrail_codes: tuple[str, ...] = ()
    human_approval_id: UUID | None = None
    change_summary: str = ""
    status_reason: str = ""
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _require_text(self.name, "Blueprint name")
        _require_text(self.business_need, "Business need")
        _require_text(self.role, "Agent role")
        _require_text(self.objective, "Agent objective")
        _require_text_tuple(self.allowed_actions, "Allowed actions")
        _require_text_tuple(self.prohibited_actions, "Prohibited actions")
        _require_text_tuple(self.logs_required, "Required logs")
        _require_text(self.rollback_procedure, "Rollback procedure")
        _require_text(self.disable_procedure, "Disable procedure")
        if self.version < 1:
            raise ValueError("Blueprint version must be at least 1")
        if not self.tools:
            raise ValueError("A blueprint requires at least one explicitly permitted tool")
        if not self.approval_points:
            raise ValueError("A blueprint requires at least one human approval point")
        if not self.aria_test_plan:
            raise ValueError("A blueprint requires an ARIA test plan")

        normalized_actions = tuple(_normalize(action) for action in self.allowed_actions)
        if any(action == "*" for action in normalized_actions):
            raise ValueError("Wildcard actions are not allowed")
        for action in normalized_actions:
            if any(fragment in action for fragment in _FORBIDDEN_ACTION_FRAGMENTS):
                raise ValueError(f"Action {action!r} violates the OAAA v0.1 safety boundary")

        mutating = any(
            fragment in action
            for action in normalized_actions
            for fragment in _MUTATING_ACTION_FRAGMENTS
        )
        if mutating and not self.approval_points:
            raise ValueError("Mutating actions require explicit human approval points")

        families = {requirement.family for requirement in self.aria_test_plan}
        missing_families = _REQUIRED_ARIA_FAMILIES - families
        if missing_families:
            missing = ", ".join(sorted(family.value for family in missing_families))
            raise ValueError(f"ARIA plan is missing required families: {missing}")

        if self.status in {
            BlueprintStatus.CLEARED,
            BlueprintStatus.APPROVED,
            BlueprintStatus.ACTIVE,
        }:
            if self.clearance_result_id is None or self.clearance_decision is None:
                raise ValueError(f"Status {self.status.value} requires a recorded Aegis clearance")
        if self.status in {BlueprintStatus.APPROVED, BlueprintStatus.ACTIVE}:
            if self.human_approval_id is None:
                raise ValueError(f"Status {self.status.value} requires named human approval")
        if (
            self.clearance_decision == ClearanceDecision.APTO_CON_CONTROLES
            and not self.clearance_conditions
        ):
            raise ValueError("APTO CON CONTROLES requires explicit clearance conditions")

    def safety_payload(self) -> dict[str, Any]:
        return {
            "case_id": str(self.case_id),
            "organization_id": str(self.organization_id),
            "owner_id": str(self.owner_id),
            "name": self.name.strip(),
            "business_need": self.business_need.strip(),
            "role": self.role.strip(),
            "objective": self.objective.strip(),
            "tools": [tool.to_dict() for tool in self.tools],
            "data_boundary": self.data_boundary.to_dict(),
            "allowed_actions": list(self.allowed_actions),
            "prohibited_actions": list(self.prohibited_actions),
            "autonomy_level": self.autonomy_level.value,
            "approval_points": [point.to_dict() for point in self.approval_points],
            "logs_required": list(self.logs_required),
            "aria_test_plan": [requirement.to_dict() for requirement in self.aria_test_plan],
            "rollback_procedure": self.rollback_procedure.strip(),
            "disable_procedure": self.disable_procedure.strip(),
            "sensitivity": self.sensitivity.value,
        }

    @property
    def safety_fingerprint(self) -> str:
        return sha256(_canonical_json(self.safety_payload()).encode("utf-8")).hexdigest()

    def integrity_payload(self) -> dict[str, Any]:
        return {
            **self.safety_payload(),
            "blueprint_id": str(self.blueprint_id),
            "version": self.version,
            "status": self.status.value,
            "material_change": self.material_change,
            "clearance_result_id": (
                str(self.clearance_result_id) if self.clearance_result_id else None
            ),
            "clearance_decision": (
                self.clearance_decision.value if self.clearance_decision else None
            ),
            "clearance_conditions": list(self.clearance_conditions),
            "clearance_guardrail_codes": list(self.clearance_guardrail_codes),
            "human_approval_id": str(self.human_approval_id) if self.human_approval_id else None,
            "change_summary": self.change_summary.strip(),
            "status_reason": self.status_reason.strip(),
        }

    @property
    def integrity_hash(self) -> str:
        return sha256(_canonical_json(self.integrity_payload()).encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "blueprint_id": str(self.blueprint_id),
            "case_id": str(self.case_id),
            "organization_id": str(self.organization_id),
            "owner_id": str(self.owner_id),
            "created_by": str(self.created_by),
            "version": self.version,
            "status": self.status.value,
            "material_change": self.material_change,
            "vault_artifact_id": str(self.vault_artifact_id) if self.vault_artifact_id else None,
            "parent_version_id": str(self.parent_version_id) if self.parent_version_id else None,
            "clearance_result_id": (
                str(self.clearance_result_id) if self.clearance_result_id else None
            ),
            "clearance_decision": (
                self.clearance_decision.value if self.clearance_decision else None
            ),
            "clearance_conditions": list(self.clearance_conditions),
            "clearance_guardrail_codes": list(self.clearance_guardrail_codes),
            "human_approval_id": str(self.human_approval_id) if self.human_approval_id else None,
            "change_summary": self.change_summary,
            "status_reason": self.status_reason,
            "safety_fingerprint": self.safety_fingerprint,
            "integrity_hash": self.integrity_hash,
            "created_at": self.created_at.isoformat(),
            **self.safety_payload(),
        }


@dataclass(frozen=True, slots=True)
class HumanApprovalRecord:
    blueprint_id: UUID
    blueprint_version_id: UUID
    blueprint_fingerprint: str
    approver_id: UUID
    decision: HumanDecision
    rationale: str
    clearance_result_id: UUID
    vault_receipt_id: UUID
    vault_receipt_hash: str
    id: UUID = field(default_factory=uuid4)
    conditions: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _require_text(self.blueprint_fingerprint, "Blueprint fingerprint")
        _require_text(self.rationale, "Approval rationale")
        _require_text(self.vault_receipt_hash, "Vault receipt hash")
        if self.decision == HumanDecision.APPROVE_WITH_CONDITIONS and not self.conditions:
            raise ValueError("Conditional human approval requires at least one condition")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "blueprint_id": str(self.blueprint_id),
            "blueprint_version_id": str(self.blueprint_version_id),
            "blueprint_fingerprint": self.blueprint_fingerprint,
            "approver_id": str(self.approver_id),
            "decision": self.decision.value,
            "rationale": self.rationale.strip(),
            "conditions": list(self.conditions),
            "clearance_result_id": str(self.clearance_result_id),
            "vault_receipt_id": str(self.vault_receipt_id),
            "vault_receipt_hash": self.vault_receipt_hash,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class ActivationReceipt:
    blueprint_id: UUID
    blueprint_version_id: UUID
    blueprint_fingerprint: str
    clearance_result_id: UUID
    clearance_decision: ClearanceDecision
    human_approval_id: UUID
    activated_by: UUID
    activation_note: str
    vault_receipt_id: UUID
    vault_receipt_hash: str
    methodology_version: str = "OAAA-BLUEPRINT-0.1"
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _require_text(self.blueprint_fingerprint, "Blueprint fingerprint")
        _require_text(self.activation_note, "Activation note")
        _require_text(self.vault_receipt_hash, "Vault receipt hash")
        _require_text(self.methodology_version, "Methodology version")

    def integrity_payload(self) -> dict[str, Any]:
        return {
            "blueprint_id": str(self.blueprint_id),
            "blueprint_version_id": str(self.blueprint_version_id),
            "blueprint_fingerprint": self.blueprint_fingerprint,
            "clearance_result_id": str(self.clearance_result_id),
            "clearance_decision": self.clearance_decision.value,
            "human_approval_id": str(self.human_approval_id),
            "activated_by": str(self.activated_by),
            "activation_note": self.activation_note.strip(),
            "vault_receipt_id": str(self.vault_receipt_id),
            "vault_receipt_hash": self.vault_receipt_hash,
            "methodology_version": self.methodology_version,
        }

    @property
    def receipt_hash(self) -> str:
        return sha256(_canonical_json(self.integrity_payload()).encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            **self.integrity_payload(),
            "receipt_hash": self.receipt_hash,
            "created_at": self.created_at.isoformat(),
        }

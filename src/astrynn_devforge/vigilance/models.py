from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any
from uuid import UUID, uuid4

from astrynn_devforge.kernel import Sensitivity

from .enums import (
    ApprovalDecision,
    AuthorizationOutcome,
    GrantStatus,
    PermissionAction,
    PermissionEventType,
)

_SENSITIVE_ACTIONS = {
    PermissionAction.SEND,
    PermissionAction.DELETE,
    PermissionAction.EXECUTE,
}


def utc_now() -> datetime:
    return datetime.now(UTC)


def _require_text(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True, slots=True)
class PermissionGrantVersion:
    grant_id: UUID
    case_id: UUID
    blueprint_id: UUID
    blueprint_version_id: UUID
    blueprint_fingerprint: str
    subject_id: UUID
    owner_id: UUID
    created_by: UUID
    tool_name: str
    resource_prefixes: tuple[str, ...]
    allowed_actions: tuple[PermissionAction, ...]
    denied_actions: tuple[PermissionAction, ...]
    approval_required_actions: tuple[PermissionAction, ...]
    sensitivity: Sensitivity
    version: int
    status: GrantStatus
    reason: str
    review_at: datetime
    expires_at: datetime
    id: UUID = field(default_factory=uuid4)
    parent_version_id: UUID | None = None
    approved_by: UUID | None = None
    activated_at: datetime | None = None
    emergency_disabled: bool = False
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _require_text(self.blueprint_fingerprint, "Blueprint fingerprint")
        _require_text(self.tool_name, "Tool name")
        _require_text(self.reason, "Permission reason")
        if self.version < 1:
            raise ValueError("Permission grant version must be at least 1")
        if not self.resource_prefixes:
            raise ValueError("At least one explicit resource prefix is required")
        for prefix in self.resource_prefixes:
            _require_text(prefix, "Resource prefix")
            if prefix.strip() == "*" or "*" in prefix:
                raise ValueError("Wildcard resource prefixes are not allowed")
        if not self.allowed_actions:
            raise ValueError("At least one explicit action is required")
        if len(set(self.allowed_actions)) != len(self.allowed_actions):
            raise ValueError("Allowed actions must be unique")
        if len(set(self.denied_actions)) != len(self.denied_actions):
            raise ValueError("Denied actions must be unique")
        if set(self.allowed_actions) & set(self.denied_actions):
            raise ValueError("An action cannot be both allowed and denied")
        if not set(self.approval_required_actions).issubset(set(self.allowed_actions)):
            raise ValueError("Approval-required actions must also be explicitly allowed")
        missing_gates = (_SENSITIVE_ACTIONS & set(self.allowed_actions)) - set(
            self.approval_required_actions
        )
        if missing_gates:
            missing = ", ".join(sorted(action.value for action in missing_gates))
            raise ValueError(f"Sensitive actions require human approval: {missing}")
        if self.review_at <= self.created_at:
            raise ValueError("Review date must be after grant creation")
        if self.expires_at <= self.created_at:
            raise ValueError("Expiry date must be after grant creation")
        if self.expires_at < self.review_at:
            raise ValueError("Expiry date cannot precede the review date")
        if self.status == GrantStatus.ACTIVE and (
            self.approved_by is None or self.activated_at is None
        ):
            raise ValueError("ACTIVE grants require a named approver and activation time")
        if self.emergency_disabled and self.status != GrantStatus.SUSPENDED:
            raise ValueError("Emergency-disabled grants must be SUSPENDED")

    def permission_payload(self) -> dict[str, Any]:
        return {
            "case_id": str(self.case_id),
            "blueprint_id": str(self.blueprint_id),
            "blueprint_version_id": str(self.blueprint_version_id),
            "blueprint_fingerprint": self.blueprint_fingerprint,
            "subject_id": str(self.subject_id),
            "owner_id": str(self.owner_id),
            "tool_name": self.tool_name.strip(),
            "resource_prefixes": list(self.resource_prefixes),
            "allowed_actions": [action.value for action in self.allowed_actions],
            "denied_actions": [action.value for action in self.denied_actions],
            "approval_required_actions": [
                action.value for action in self.approval_required_actions
            ],
            "sensitivity": self.sensitivity.value,
            "review_at": self.review_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }

    @property
    def permission_fingerprint(self) -> str:
        return sha256(_canonical_json(self.permission_payload()).encode("utf-8")).hexdigest()

    def integrity_payload(self) -> dict[str, Any]:
        return {
            **self.permission_payload(),
            "grant_id": str(self.grant_id),
            "version": self.version,
            "status": self.status.value,
            "reason": self.reason.strip(),
            "parent_version_id": (
                str(self.parent_version_id) if self.parent_version_id else None
            ),
            "approved_by": str(self.approved_by) if self.approved_by else None,
            "activated_at": self.activated_at.isoformat() if self.activated_at else None,
            "emergency_disabled": self.emergency_disabled,
        }

    @property
    def integrity_hash(self) -> str:
        return sha256(_canonical_json(self.integrity_payload()).encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "created_by": str(self.created_by),
            "created_at": self.created_at.isoformat(),
            "permission_fingerprint": self.permission_fingerprint,
            "integrity_hash": self.integrity_hash,
            **self.integrity_payload(),
        }


@dataclass(frozen=True, slots=True)
class PermissionApprovalRequest:
    grant_id: UUID
    grant_version_id: UUID
    grant_permission_fingerprint: str
    case_id: UUID
    subject_id: UUID
    requested_by: UUID
    action: PermissionAction
    resource: str
    justification: str
    expires_at: datetime
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _require_text(self.grant_permission_fingerprint, "Grant permission fingerprint")
        _require_text(self.resource, "Requested resource")
        _require_text(self.justification, "Approval justification")
        if self.expires_at <= self.created_at:
            raise ValueError("Approval request expiry must be in the future")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "grant_id": str(self.grant_id),
            "grant_version_id": str(self.grant_version_id),
            "grant_permission_fingerprint": self.grant_permission_fingerprint,
            "case_id": str(self.case_id),
            "subject_id": str(self.subject_id),
            "requested_by": str(self.requested_by),
            "action": self.action.value,
            "resource": self.resource.strip(),
            "justification": self.justification.strip(),
            "expires_at": self.expires_at.isoformat(),
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class PermissionApprovalRecord:
    request_id: UUID
    grant_id: UUID
    grant_version_id: UUID
    grant_permission_fingerprint: str
    approver_id: UUID
    decision: ApprovalDecision
    rationale: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _require_text(self.grant_permission_fingerprint, "Grant permission fingerprint")
        _require_text(self.rationale, "Approval rationale")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "request_id": str(self.request_id),
            "grant_id": str(self.grant_id),
            "grant_version_id": str(self.grant_version_id),
            "grant_permission_fingerprint": self.grant_permission_fingerprint,
            "approver_id": str(self.approver_id),
            "decision": self.decision.value,
            "rationale": self.rationale.strip(),
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class PermissionGrantReceipt:
    grant_id: UUID
    grant_version_id: UUID
    case_id: UUID
    blueprint_id: UUID
    blueprint_version_id: UUID
    blueprint_fingerprint: str
    permission_fingerprint: str
    grant_integrity_hash: str
    approved_by: UUID
    activated_at: datetime
    methodology_version: str = "VIGILANCE-PERMISSIONS-0.1"
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _require_text(self.blueprint_fingerprint, "Blueprint fingerprint")
        _require_text(self.permission_fingerprint, "Permission fingerprint")
        _require_text(self.grant_integrity_hash, "Grant integrity hash")
        _require_text(self.methodology_version, "Methodology version")

    def integrity_payload(self) -> dict[str, Any]:
        return {
            "grant_id": str(self.grant_id),
            "grant_version_id": str(self.grant_version_id),
            "case_id": str(self.case_id),
            "blueprint_id": str(self.blueprint_id),
            "blueprint_version_id": str(self.blueprint_version_id),
            "blueprint_fingerprint": self.blueprint_fingerprint,
            "permission_fingerprint": self.permission_fingerprint,
            "grant_integrity_hash": self.grant_integrity_hash,
            "approved_by": str(self.approved_by),
            "activated_at": self.activated_at.isoformat(),
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


@dataclass(frozen=True, slots=True)
class ActionAuthorizationReceipt:
    grant_id: UUID
    grant_version_id: UUID
    grant_permission_fingerprint: str
    case_id: UUID
    subject_id: UUID
    action: PermissionAction
    resource: str
    outcome: AuthorizationOutcome
    reason: str
    evaluated_by: UUID
    approval_request_id: UUID | None = None
    approval_record_id: UUID | None = None
    methodology_version: str = "VIGILANCE-PERMISSIONS-0.1"
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _require_text(self.grant_permission_fingerprint, "Grant permission fingerprint")
        _require_text(self.resource, "Authorization resource")
        _require_text(self.reason, "Authorization reason")
        _require_text(self.methodology_version, "Methodology version")

    def integrity_payload(self) -> dict[str, Any]:
        return {
            "grant_id": str(self.grant_id),
            "grant_version_id": str(self.grant_version_id),
            "grant_permission_fingerprint": self.grant_permission_fingerprint,
            "case_id": str(self.case_id),
            "subject_id": str(self.subject_id),
            "action": self.action.value,
            "resource": self.resource.strip(),
            "outcome": self.outcome.value,
            "reason": self.reason.strip(),
            "evaluated_by": str(self.evaluated_by),
            "approval_request_id": (
                str(self.approval_request_id) if self.approval_request_id else None
            ),
            "approval_record_id": (
                str(self.approval_record_id) if self.approval_record_id else None
            ),
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


@dataclass(frozen=True, slots=True)
class PermissionEvent:
    case_id: UUID
    grant_id: UUID
    event_type: PermissionEventType
    actor_id: UUID
    details: dict[str, Any]
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "case_id": str(self.case_id),
            "grant_id": str(self.grant_id),
            "event_type": self.event_type.value,
            "actor_id": str(self.actor_id),
            "details": self.details,
            "created_at": self.created_at.isoformat(),
        }

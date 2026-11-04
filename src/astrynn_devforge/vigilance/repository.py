from __future__ import annotations

from copy import deepcopy
from threading import Lock
from uuid import UUID

from .enums import AuthorizationOutcome, PermissionEventType
from .models import (
    ActionAuthorizationReceipt,
    PermissionApprovalRecord,
    PermissionApprovalRequest,
    PermissionEvent,
    PermissionGrantReceipt,
    PermissionGrantVersion,
    utc_now,
)


class PermissionGrantNotFoundError(KeyError):
    pass


class DuplicatePermissionVersionError(ValueError):
    pass


class StaleAuthorizationGrantError(ValueError):
    pass


class InvalidStoredAuthorizationReceiptError(ValueError):
    pass


class PermissionRequestNotFoundError(KeyError):
    pass


class InMemoryVigilanceRepository:
    """Append-only development store for grants, approvals, receipts, and events."""

    def __init__(self) -> None:
        self._grant_receipt_lock = Lock()
        self._versions: dict[UUID, list[PermissionGrantVersion]] = {}
        self._requests: dict[UUID, PermissionApprovalRequest] = {}
        self._approval_records: list[PermissionApprovalRecord] = []
        self._grant_receipts: list[PermissionGrantReceipt] = []
        self._authorization_receipts: list[ActionAuthorizationReceipt] = []
        self._events: list[PermissionEvent] = []

    def append_version(self, grant: PermissionGrantVersion) -> PermissionGrantVersion:
        with self._grant_receipt_lock:
            versions = self._versions.setdefault(grant.grant_id, [])
            expected_version = len(versions) + 1
            if grant.version != expected_version:
                raise DuplicatePermissionVersionError(
                    f"Expected permission version {expected_version}, got {grant.version}"
                )
            if versions and grant.parent_version_id != versions[-1].id:
                raise DuplicatePermissionVersionError(
                    "A new permission version must reference the previous version"
                )
            if not versions and grant.parent_version_id is not None:
                raise DuplicatePermissionVersionError(
                    "The first permission version cannot have a parent"
                )
            versions.append(deepcopy(grant))
            return deepcopy(grant)

    def latest_version(self, grant_id: UUID) -> PermissionGrantVersion:
        with self._grant_receipt_lock:
            versions = self._versions.get(grant_id)
            if not versions:
                raise PermissionGrantNotFoundError(str(grant_id))
            return deepcopy(versions[-1])

    def versions_for_grant(self, grant_id: UUID) -> tuple[PermissionGrantVersion, ...]:
        with self._grant_receipt_lock:
            versions = self._versions.get(grant_id)
            if not versions:
                raise PermissionGrantNotFoundError(str(grant_id))
            return tuple(deepcopy(item) for item in versions)

    def append_request(self, request: PermissionApprovalRequest) -> PermissionApprovalRequest:
        if request.id in self._requests:
            raise ValueError(f"Approval request {request.id} already exists")
        self._requests[request.id] = deepcopy(request)
        return deepcopy(request)

    def get_request(self, request_id: UUID) -> PermissionApprovalRequest:
        try:
            return deepcopy(self._requests[request_id])
        except KeyError as exc:
            raise PermissionRequestNotFoundError(str(request_id)) from exc

    def requests_for_grant(self, grant_id: UUID) -> tuple[PermissionApprovalRequest, ...]:
        matches = [item for item in self._requests.values() if item.grant_id == grant_id]
        return tuple(deepcopy(item) for item in sorted(matches, key=lambda item: item.created_at))

    def append_approval_record(
        self, record: PermissionApprovalRecord
    ) -> PermissionApprovalRecord:
        if any(item.id == record.id for item in self._approval_records):
            raise ValueError(f"Approval record {record.id} already exists")
        self._approval_records.append(deepcopy(record))
        return deepcopy(record)

    def decisions_for_request(self, request_id: UUID) -> tuple[PermissionApprovalRecord, ...]:
        return tuple(
            deepcopy(item)
            for item in self._approval_records
            if item.request_id == request_id
        )

    def append_grant_receipt(self, receipt: PermissionGrantReceipt) -> PermissionGrantReceipt:
        if any(item.id == receipt.id for item in self._grant_receipts):
            raise ValueError(f"Grant receipt {receipt.id} already exists")
        self._grant_receipts.append(deepcopy(receipt))
        return deepcopy(receipt)

    def grant_receipts_for_grant(self, grant_id: UUID) -> tuple[PermissionGrantReceipt, ...]:
        return tuple(
            deepcopy(item)
            for item in self._grant_receipts
            if item.grant_id == grant_id
        )

    def append_authorization_receipt(
        self, receipt: ActionAuthorizationReceipt
    ) -> ActionAuthorizationReceipt:
        with self._grant_receipt_lock:
            return self._append_authorization_receipt_unlocked(receipt)

    def _append_authorization_receipt_unlocked(
        self, receipt: ActionAuthorizationReceipt
    ) -> ActionAuthorizationReceipt:
        if any(item.id == receipt.id for item in self._authorization_receipts):
            raise ValueError(f"Authorization receipt {receipt.id} already exists")
        self._authorization_receipts.append(deepcopy(receipt))
        return deepcopy(receipt)

    def append_authorization_receipt_if_current(
        self, receipt: ActionAuthorizationReceipt
    ) -> ActionAuthorizationReceipt:
        """Compare and append atomically within this in-memory repository instance."""
        with self._grant_receipt_lock:
            versions = self._versions.get(receipt.grant_id)
            if not versions:
                raise PermissionGrantNotFoundError(str(receipt.grant_id))
            latest = versions[-1]
            if (
                latest.id != receipt.grant_version_id
                or latest.permission_fingerprint != receipt.grant_permission_fingerprint
                or latest.case_id != receipt.case_id
            ):
                raise StaleAuthorizationGrantError("Grant changed before receipt storage")
            if receipt.outcome is AuthorizationOutcome.ALLOWED:
                now = utc_now()
                if now >= latest.review_at or now >= latest.expires_at:
                    raise StaleAuthorizationGrantError("Grant deadline passed before receipt storage")
            return self._append_authorization_receipt_unlocked(receipt)

    def authorization_receipts_for_grant(
        self, grant_id: UUID
    ) -> tuple[ActionAuthorizationReceipt, ...]:
        with self._grant_receipt_lock:
            return tuple(
                deepcopy(item)
                for item in self._authorization_receipts
                if item.grant_id == grant_id
            )

    def append_event(self, event: PermissionEvent) -> PermissionEvent:
        with self._grant_receipt_lock:
            return self._append_event_unlocked(event)

    def _append_event_unlocked(self, event: PermissionEvent) -> PermissionEvent:
        if any(item.id == event.id for item in self._events):
            raise ValueError(f"Permission event {event.id} already exists")
        self._events.append(deepcopy(event))
        return deepcopy(event)

    def events_for_grant(self, grant_id: UUID) -> tuple[PermissionEvent, ...]:
        with self._grant_receipt_lock:
            return tuple(
                deepcopy(item)
                for item in self._events
                if item.grant_id == grant_id
            )

    def append_action_event_if_current(
        self, authorization: ActionAuthorizationReceipt, event: PermissionEvent
    ) -> PermissionEvent:
        """Check grant and stored receipt while appending an in-process event."""
        with self._grant_receipt_lock:
            versions = self._versions.get(authorization.grant_id)
            if not versions:
                raise PermissionGrantNotFoundError(str(authorization.grant_id))
            latest = versions[-1]
            if (
                latest.id != authorization.grant_version_id
                or latest.permission_fingerprint != authorization.grant_permission_fingerprint
                or latest.case_id != authorization.case_id
            ):
                raise StaleAuthorizationGrantError("Grant changed before action recording")
            matches = [
                item for item in self._authorization_receipts
                if item.grant_id == authorization.grant_id and item.id == authorization.id
            ]
            if (
                authorization.outcome is not AuthorizationOutcome.ALLOWED
                or len(matches) != 1
                or matches[0] != authorization
            ):
                raise InvalidStoredAuthorizationReceiptError("Stored authorization mismatch")
            evaluations = [
                item for item in self._events
                if item.event_type is PermissionEventType.AUTHORIZATION_EVALUATED
                and item.details.get("authorization_receipt_id") == str(authorization.id)
            ]
            if len(evaluations) != 1:
                raise InvalidStoredAuthorizationReceiptError("Authorization evaluation missing")
            evaluation = evaluations[0]
            if (
                evaluation.grant_id != authorization.grant_id
                or evaluation.case_id != authorization.case_id
                or evaluation.actor_id != authorization.evaluated_by
                or evaluation.details.get("outcome") != authorization.outcome.value
                or evaluation.details.get("action") != authorization.action.value
                or evaluation.details.get("resource") != authorization.resource.strip()
                or evaluation.details.get("reason") != authorization.reason
            ):
                raise InvalidStoredAuthorizationReceiptError("Authorization evaluation mismatch")
            if (
                event.grant_id != authorization.grant_id
                or event.case_id != authorization.case_id
                or event.event_type is not PermissionEventType.ACTION_RECORDED
                or event.details.get("authorization_receipt_id") != str(authorization.id)
                or event.details.get("authorization_receipt_hash") != authorization.receipt_hash
            ):
                raise ValueError("Action event does not match its authorization")
            return self._append_event_unlocked(event)

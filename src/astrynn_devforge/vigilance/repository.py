from __future__ import annotations

from copy import deepcopy
from uuid import UUID

from .models import (
    ActionAuthorizationReceipt,
    PermissionApprovalRecord,
    PermissionApprovalRequest,
    PermissionEvent,
    PermissionGrantReceipt,
    PermissionGrantVersion,
)


class PermissionGrantNotFoundError(KeyError):
    pass


class DuplicatePermissionVersionError(ValueError):
    pass


class PermissionRequestNotFoundError(KeyError):
    pass


class InMemoryVigilanceRepository:
    """Append-only development store for grants, approvals, receipts, and events."""

    def __init__(self) -> None:
        self._versions: dict[UUID, list[PermissionGrantVersion]] = {}
        self._requests: dict[UUID, PermissionApprovalRequest] = {}
        self._approval_records: list[PermissionApprovalRecord] = []
        self._grant_receipts: list[PermissionGrantReceipt] = []
        self._authorization_receipts: list[ActionAuthorizationReceipt] = []
        self._events: list[PermissionEvent] = []

    def append_version(self, grant: PermissionGrantVersion) -> PermissionGrantVersion:
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
        versions = self._versions.get(grant_id)
        if not versions:
            raise PermissionGrantNotFoundError(str(grant_id))
        return deepcopy(versions[-1])

    def versions_for_grant(self, grant_id: UUID) -> tuple[PermissionGrantVersion, ...]:
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
        if any(item.id == receipt.id for item in self._authorization_receipts):
            raise ValueError(f"Authorization receipt {receipt.id} already exists")
        self._authorization_receipts.append(deepcopy(receipt))
        return deepcopy(receipt)

    def authorization_receipts_for_grant(
        self, grant_id: UUID
    ) -> tuple[ActionAuthorizationReceipt, ...]:
        return tuple(
            deepcopy(item)
            for item in self._authorization_receipts
            if item.grant_id == grant_id
        )

    def append_event(self, event: PermissionEvent) -> PermissionEvent:
        if any(item.id == event.id for item in self._events):
            raise ValueError(f"Permission event {event.id} already exists")
        self._events.append(deepcopy(event))
        return deepcopy(event)

    def events_for_grant(self, grant_id: UUID) -> tuple[PermissionEvent, ...]:
        return tuple(
            deepcopy(item)
            for item in self._events
            if item.grant_id == grant_id
        )

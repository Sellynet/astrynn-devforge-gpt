from __future__ import annotations

from copy import deepcopy
from uuid import UUID

from .models import ActivationReceipt, AgentBlueprintVersion, HumanApprovalRecord


class BlueprintNotFoundError(KeyError):
    pass


class DuplicateBlueprintVersionError(ValueError):
    pass


class InMemoryAgentBlueprintRepository:
    """Development repository with append-only blueprint and approval history."""

    def __init__(self) -> None:
        self._versions: dict[UUID, list[AgentBlueprintVersion]] = {}
        self._approvals: list[HumanApprovalRecord] = []
        self._activation_receipts: list[ActivationReceipt] = []

    def append_version(self, blueprint: AgentBlueprintVersion) -> AgentBlueprintVersion:
        versions = self._versions.setdefault(blueprint.blueprint_id, [])
        expected_version = len(versions) + 1
        if blueprint.version != expected_version:
            raise DuplicateBlueprintVersionError(
                f"Expected blueprint version {expected_version}, got {blueprint.version}"
            )
        if versions and blueprint.parent_version_id != versions[-1].id:
            raise DuplicateBlueprintVersionError(
                "A new blueprint version must reference the previous version"
            )
        if not versions and blueprint.parent_version_id is not None:
            raise DuplicateBlueprintVersionError(
                "The first blueprint version cannot have a parent version"
            )
        versions.append(deepcopy(blueprint))
        return deepcopy(blueprint)

    def latest_version(self, blueprint_id: UUID) -> AgentBlueprintVersion:
        versions = self._versions.get(blueprint_id)
        if not versions:
            raise BlueprintNotFoundError(str(blueprint_id))
        return deepcopy(versions[-1])

    def versions_for_blueprint(self, blueprint_id: UUID) -> tuple[AgentBlueprintVersion, ...]:
        versions = self._versions.get(blueprint_id)
        if not versions:
            raise BlueprintNotFoundError(str(blueprint_id))
        return tuple(deepcopy(version) for version in versions)

    def append_approval(self, approval: HumanApprovalRecord) -> HumanApprovalRecord:
        self._approvals.append(deepcopy(approval))
        return deepcopy(approval)

    def approvals_for_blueprint(self, blueprint_id: UUID) -> tuple[HumanApprovalRecord, ...]:
        return tuple(
            deepcopy(record)
            for record in self._approvals
            if record.blueprint_id == blueprint_id
        )

    def append_activation_receipt(self, receipt: ActivationReceipt) -> ActivationReceipt:
        self._activation_receipts.append(deepcopy(receipt))
        return deepcopy(receipt)

    def activation_receipts_for_blueprint(
        self, blueprint_id: UUID
    ) -> tuple[ActivationReceipt, ...]:
        return tuple(
            deepcopy(receipt)
            for receipt in self._activation_receipts
            if receipt.blueprint_id == blueprint_id
        )

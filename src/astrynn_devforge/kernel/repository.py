from __future__ import annotations

from collections.abc import Iterable
from copy import deepcopy
from typing import Protocol, runtime_checkable
from uuid import UUID

from .models import ApprovalRecord, Case, EvidenceReference, OutputArtifact


class CaseNotFoundError(KeyError):
    pass


def approval_event_matches(case: Case, approval: ApprovalRecord) -> bool:
    """Check lineage consistency; this is not authentication of the approver."""
    if case.id != approval.case_id:
        return False
    events = [
        event for event in case.events
        if event.event_type == "APPROVAL_RECORDED"
        and event.details.get("approval_id") == str(approval.id)
    ]
    return len(events) == 1 and (
        events[0].actor_id == approval.approver_id
        and events[0].details.get("decision") == approval.decision.value
        and events[0].details.get("conditions") == list(approval.conditions)
    )


@runtime_checkable
class KernelRepository(Protocol):
    """Persistence contract shared by in-memory and SQL-backed adapters."""

    @property
    def persistence_name(self) -> str: ...

    def save_case(self, case: Case) -> Case: ...

    def get_case(self, case_id: UUID) -> Case: ...

    def list_cases(self) -> list[Case]: ...

    def append_approval(self, approval: ApprovalRecord) -> ApprovalRecord: ...

    def commit_approval_and_case(self, approval: ApprovalRecord, case: Case) -> ApprovalRecord: ...

    def approvals_for_case(self, case_id: UUID) -> tuple[ApprovalRecord, ...]: ...

    def append_evidence(self, evidence: EvidenceReference) -> EvidenceReference: ...

    def evidence_for_case(self, case_id: UUID) -> tuple[EvidenceReference, ...]: ...

    def append_output(self, output: OutputArtifact) -> OutputArtifact: ...

    def outputs_for_case(self, case_id: UUID) -> tuple[OutputArtifact, ...]: ...


class InMemoryKernelRepository:
    """Development repository with defensive copies and append-only audit records."""

    def __init__(self) -> None:
        self._cases: dict[UUID, Case] = {}
        self._approvals: list[ApprovalRecord] = []
        self._evidence: list[EvidenceReference] = []
        self._outputs: list[OutputArtifact] = []

    @property
    def persistence_name(self) -> str:
        return "in-memory-development"

    def save_case(self, case: Case) -> Case:
        self._cases[case.id] = deepcopy(case)
        return deepcopy(case)

    def get_case(self, case_id: UUID) -> Case:
        try:
            return deepcopy(self._cases[case_id])
        except KeyError as exc:
            raise CaseNotFoundError(str(case_id)) from exc

    def list_cases(self) -> list[Case]:
        return [deepcopy(case) for case in self._cases.values()]

    def append_approval(self, approval: ApprovalRecord) -> ApprovalRecord:
        self._approvals.append(approval)
        return approval

    def commit_approval_and_case(self, approval: ApprovalRecord, case: Case) -> ApprovalRecord:
        if case.id not in self._cases:
            raise CaseNotFoundError(str(case.id))
        if not approval_event_matches(case, approval):
            raise ValueError("Approval requires one matching case event")
        if any(existing.id == approval.id for existing in self._approvals):
            raise ValueError("Approval already exists")
        # Development-only in-memory store, not durable cross-process atomicity.
        self._cases[case.id] = deepcopy(case)
        self._approvals.append(deepcopy(approval))
        return deepcopy(approval)

    def approvals_for_case(self, case_id: UUID) -> tuple[ApprovalRecord, ...]:
        return tuple(record for record in self._approvals if record.case_id == case_id)

    def append_evidence(self, evidence: EvidenceReference) -> EvidenceReference:
        self._evidence.append(evidence)
        return evidence

    def evidence_for_case(self, case_id: UUID) -> tuple[EvidenceReference, ...]:
        return tuple(record for record in self._evidence if record.case_id == case_id)

    def append_output(self, output: OutputArtifact) -> OutputArtifact:
        self._outputs.append(output)
        return output

    def outputs_for_case(self, case_id: UUID) -> tuple[OutputArtifact, ...]:
        return tuple(record for record in self._outputs if record.case_id == case_id)

    @staticmethod
    def count(records: Iterable[object]) -> int:
        return sum(1 for _ in records)

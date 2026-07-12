from pathlib import Path
from uuid import uuid4

import pytest

from astrynn_devforge.kernel import (
    ApprovalDecision,
    ApprovalRecord,
    ArtifactStatus,
    CaseNotFoundError,
    EvidenceReference,
    KernelRepository,
    KernelService,
    OutputArtifact,
    Sensitivity,
)
from astrynn_devforge.persistence import SQLAlchemyKernelRepository


def sqlite_url(path: Path) -> str:
    return f"sqlite:///{path.as_posix()}"


def build_repository(path: Path) -> SQLAlchemyKernelRepository:
    return SQLAlchemyKernelRepository(sqlite_url(path), create_schema=True)


def create_case(repository: SQLAlchemyKernelRepository):
    owner_id = uuid4()
    organization_id = uuid4()
    case = KernelService(repository).create_case(
        title="Persistent governed case",
        description="Synthetic persistence test",
        owner_id=owner_id,
        organization_id=organization_id,
        sensitivity=Sensitivity.ORANGE,
        actor_id=owner_id,
    )
    return case


def test_sqlalchemy_repository_satisfies_kernel_contract(tmp_path: Path) -> None:
    repository = build_repository(tmp_path / "contract.db")

    assert isinstance(repository, KernelRepository)
    assert repository.persistence_name == "sqlalchemy-sqlite"


def test_case_and_events_survive_repository_restart(tmp_path: Path) -> None:
    database = tmp_path / "restart.db"
    first = build_repository(database)
    case = create_case(first)
    first.close()

    second = SQLAlchemyKernelRepository(sqlite_url(database))
    recovered = second.get_case(case.id)

    assert recovered.id == case.id
    assert recovered.title == case.title
    assert recovered.version == case.version
    assert len(recovered.events) == 1
    assert recovered.events[0].event_type == "CASE_CREATED"


def test_resaving_case_does_not_duplicate_events(tmp_path: Path) -> None:
    repository = build_repository(tmp_path / "events.db")
    case = create_case(repository)

    repository.save_case(case)
    repository.save_case(case)
    recovered = repository.get_case(case.id)

    assert len(recovered.events) == 1


def test_append_only_collections_are_reconstructed(tmp_path: Path) -> None:
    repository = build_repository(tmp_path / "collections.db")
    case = create_case(repository)
    approver_id = uuid4()

    approval = ApprovalRecord(
        case_id=case.id,
        approver_id=approver_id,
        decision=ApprovalDecision.APPROVE_WITH_CONDITIONS,
        rationale="Synthetic approval",
        conditions=("Human gate required",),
    )
    evidence = EvidenceReference(
        case_id=case.id,
        label="ARIA receipt",
        uri="urn:astrynn:test:evidence",
        sensitivity=Sensitivity.ORANGE,
    )
    output = OutputArtifact(
        case_id=case.id,
        artifact_type="CLEARANCE_REPORT",
        owner_id=case.owner_id,
        content={"decision": "APTO_CON_CONTROLES"},
        version=1,
        status=ArtifactStatus.REVIEW,
    )

    repository.append_approval(approval)
    repository.append_evidence(evidence)
    repository.append_output(output)

    assert repository.approvals_for_case(case.id) == (approval,)
    assert repository.evidence_for_case(case.id) == (evidence,)
    assert repository.outputs_for_case(case.id) == (output,)


def test_append_methods_are_idempotent_by_record_id(tmp_path: Path) -> None:
    repository = build_repository(tmp_path / "idempotent.db")
    case = create_case(repository)
    approval = ApprovalRecord(
        case_id=case.id,
        approver_id=uuid4(),
        decision=ApprovalDecision.APPROVE,
        rationale="Recorded once",
    )

    repository.append_approval(approval)
    repository.append_approval(approval)

    assert repository.approvals_for_case(case.id) == (approval,)


def test_list_cases_returns_all_persisted_cases(tmp_path: Path) -> None:
    repository = build_repository(tmp_path / "list.db")
    first = create_case(repository)
    second = create_case(repository)

    recovered_ids = {case.id for case in repository.list_cases()}

    assert recovered_ids == {first.id, second.id}


def test_missing_case_raises_domain_error(tmp_path: Path) -> None:
    repository = build_repository(tmp_path / "missing.db")

    with pytest.raises(CaseNotFoundError):
        repository.get_case(uuid4())

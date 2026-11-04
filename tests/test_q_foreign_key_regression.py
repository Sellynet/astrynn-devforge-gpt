"""Synthetic database regressions for case/event atomicity and C08 boundaries."""

import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import OperationalError

from astrynn_devforge.kernel import (
    ApprovalDecision,
    ApprovalRequiredError,
    Case,
    CaseEvent,
    CaseNotFoundError,
    CaseStatus,
    KernelService,
    Sensitivity,
)
from astrynn_devforge.persistence.sqlalchemy_kernel import (
    CaseEventRow,
    SQLAlchemyKernelRepository,
    StaleCaseWriteError,
)


@pytest.fixture(params=("sqlite_fk", "postgresql"))
def rig(request, tmp_path):
    if request.param == "postgresql":
        url = os.getenv("ASTRYNN_POSTGRES_TEST_URL", "").strip()
        if not url:
            pytest.skip("ASTRYNN_POSTGRES_TEST_URL is not configured")
    else:
        url = f"sqlite:///{tmp_path / 'fk_enabled.db'}"
    engine = create_engine(url)
    if request.param == "sqlite_fk":
        @event.listens_for(engine, "connect")
        def enable_foreign_keys(dbapi_connection, _):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    repo = SQLAlchemyKernelRepository(url, engine=engine, create_schema=True)
    yield repo, url, request.param
    repo.close()


def make_case():
    owner = uuid4()
    case = Case(
        title="Synthetic transactional case",
        owner_id=owner,
        organization_id=uuid4(),
        sensitivity=Sensitivity.ORANGE,
    )
    case.record_event(CaseEvent(event_type="CASE_CREATED", actor_id=owner, details={}))
    return case


def test_new_case_and_event_survive_restart_with_foreign_keys(rig):
    repo, url, _backend = rig
    case = make_case()
    stored = repo.save_case(case)
    assert stored.id == case.id
    reopened = SQLAlchemyKernelRepository(url)
    try:
        restored = reopened.get_case(case.id)
        assert restored.version == 2
        assert [e.event_type for e in restored.events] == ["CASE_CREATED"]
    finally:
        reopened.close()


def test_event_failure_rolls_back_parent_case(rig):
    repo, _url, _backend = rig
    case = make_case()

    def fail_before_event(_mapper, _connection, _target):
        raise RuntimeError("injected case event insert failure")

    event.listen(CaseEventRow, "before_insert", fail_before_event)
    try:
        with pytest.raises(RuntimeError, match="injected case event"):
            repo.save_case(case)
    finally:
        event.remove(CaseEventRow, "before_insert", fail_before_event)
    with pytest.raises(CaseNotFoundError):
        repo.get_case(case.id)


def test_two_stale_writers_cannot_both_commit(rig):
    repo, _url, backend = rig
    case = repo.save_case(make_case())
    barrier = Barrier(2)

    def synchronize_update(_conn, _cursor, statement, _params, _context, _many):
        if statement.lstrip().upper().startswith("UPDATE KERNEL_CASES SET"):
            barrier.wait(timeout=10)

    event.listen(repo.engine, "before_cursor_execute", synchronize_update)

    def attempt(marker):
        instance = SQLAlchemyKernelRepository("unused", engine=repo.engine)
        snapshot = instance.get_case(case.id)
        snapshot.record_event(CaseEvent(event_type=marker, actor_id=case.owner_id, details={}))
        try:
            instance.save_case(snapshot)
            return "committed"
        except (StaleCaseWriteError, OperationalError) as exc:
            return type(exc).__name__

    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(attempt, ("RACE_A", "RACE_B")))
    finally:
        event.remove(repo.engine, "before_cursor_execute", synchronize_update)
    assert outcomes.count("committed") == 1
    if backend == "postgresql":
        assert outcomes.count("StaleCaseWriteError") == 1
    persisted = repo.get_case(case.id)
    assert sum(e.event_type in {"RACE_A", "RACE_B"} for e in persisted.events) == 1


def test_conditional_approval_stays_held_after_restart(rig):
    repo, url, _backend = rig
    case = repo.save_case(make_case())
    service = KernelService(repo)
    service.transition_case(
        case_id=case.id, target=CaseStatus.IN_REVIEW, actor_id=case.owner_id, reason="test"
    )
    approval = service.record_approval(
        case_id=case.id,
        approver_id=uuid4(),
        decision=ApprovalDecision.APPROVE_WITH_CONDITIONS,
        rationale="synthetic conditional approval",
        conditions=("verification pending",),
    )
    service.transition_case(
        case_id=case.id, target=CaseStatus.APPROVED, actor_id=case.owner_id, reason="test"
    )
    reopened = SQLAlchemyKernelRepository(url)
    try:
        assert reopened.approvals_for_case(case.id)[-1].id == approval.id
        with pytest.raises(ApprovalRequiredError):
            KernelService(reopened).transition_case(
                case_id=case.id,
                target=CaseStatus.ACTIVE,
                actor_id=case.owner_id,
                reason="must remain on hold",
            )
        restored = reopened.get_case(case.id)
        assert restored.status is CaseStatus.APPROVED
        assert sum(e.event_type == "APPROVAL_RECORDED" for e in restored.events) == 1
    finally:
        reopened.close()

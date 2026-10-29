"""Additional concurrency and transactional rollback checks on the isolated Q candidate."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError, OperationalError

from astrynn_devforge.kernel import CaseEvent, KernelService, Sensitivity
from astrynn_devforge.persistence.sqlalchemy_kernel import SQLAlchemyKernelRepository, StaleCaseWriteError


@pytest.mark.parametrize("attempt", range(10))
def test_two_writers_have_one_commit_and_no_orphan_event(tmp_path, attempt):
    url = f"sqlite:///{tmp_path / 'race.sqlite'}"
    first = SQLAlchemyKernelRepository(url, create_schema=True)
    second = SQLAlchemyKernelRepository(url)
    owner = uuid4()
    case = KernelService(first).create_case(
        title="Race", description="fixture", owner_id=owner,
        organization_id=uuid4(), sensitivity=Sensitivity.GREEN, actor_id=owner,
    )
    snapshots = [first.get_case(case.id), second.get_case(case.id)]
    for i, snapshot in enumerate(snapshots):
        snapshot.record_event(CaseEvent(event_type=f"WRITER_{i}", actor_id=owner, details={}))
    barrier = Barrier(2)

    def write(repo, snapshot):
        barrier.wait(timeout=5)
        try:
            repo.save_case(snapshot)
            return "committed"
        except (StaleCaseWriteError, OperationalError) as exc:
            return type(exc).__name__

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda args: write(*args), zip((first, second), snapshots)))
    assert results.count("committed") == 1, results
    assert any(x in {"StaleCaseWriteError", "OperationalError"} for x in results), results
    persisted = first.get_case(case.id)
    assert persisted.version == case.version + 1
    assert sum(event.event_type.startswith("WRITER_") for event in persisted.events) == 1
    first.close()
    second.close()


def test_case_update_rolls_back_if_event_insert_violates_unique_id(tmp_path):
    repo = SQLAlchemyKernelRepository(f"sqlite:///{tmp_path / 'rollback.sqlite'}", create_schema=True)
    service = KernelService(repo)
    owner = uuid4()
    def make_case(title):
        return service.create_case(title=title, description="fixture", owner_id=owner,
                                   organization_id=uuid4(), sensitivity=Sensitivity.GREEN,
                                   actor_id=owner)
    first, second = make_case("First"), make_case("Second")
    snapshot = repo.get_case(first.id)
    snapshot.record_event(CaseEvent(id=second.events[0].id, event_type="COLLISION", actor_id=owner, details={}))
    with pytest.raises(IntegrityError):
        repo.save_case(snapshot)
    persisted = repo.get_case(first.id)
    assert persisted.version == first.version
    assert [event.id for event in persisted.events] == [event.id for event in first.events]
    repo.close()

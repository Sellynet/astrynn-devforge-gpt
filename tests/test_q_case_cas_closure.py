"""Closure regression for source-aligned SQLAlchemy Kernel optimistic locking."""
from uuid import uuid4
import pytest
from astrynn_devforge.kernel import KernelService, CaseEvent, CaseStatus, Sensitivity
from astrynn_devforge.persistence.sqlalchemy_kernel import SQLAlchemyKernelRepository, StaleCaseWriteError

@pytest.fixture
def setup(tmp_path):
    url = 'sqlite:///' + str(tmp_path/'kernel.sqlite3')
    repo = SQLAlchemyKernelRepository(url, create_schema=True)
    owner,org=uuid4(),uuid4()
    svc=KernelService(repo)
    case=svc.create_case(title='Concurrencia',description='Aislamiento',owner_id=owner,
                         organization_id=org,sensitivity=Sensitivity.ORANGE,actor_id=owner)
    yield repo,svc,case.id,owner,url
    repo.close()

def test_second_writer_cannot_replace_first_commit(setup):
    repo,svc,cid,owner,url=setup
    a,b=repo.get_case(cid),repo.get_case(cid)
    a.record_event(CaseEvent(event_type='FIRST_VERIFIED',actor_id=owner,details={'source':'fixture'}))
    repo.save_case(a)
    b.status=CaseStatus.CLOSED
    b.record_event(CaseEvent(event_type='STALE_OVERWRITE',actor_id=owner,details={}))
    with pytest.raises(StaleCaseWriteError):
        repo.save_case(b)
    assert repo.get_case(cid).status==CaseStatus.DRAFT
    assert [e.event_type for e in repo.get_case(cid).events]==['CASE_CREATED','FIRST_VERIFIED']

def test_stale_save_does_not_commit_orphan_event(setup):
    repo,svc,cid,owner,url=setup
    a,b=repo.get_case(cid),repo.get_case(cid)
    a.record_event(CaseEvent(event_type='FIRST',actor_id=owner,details={}))
    repo.save_case(a)
    b.record_event(CaseEvent(event_type='REJECTED_STALE',actor_id=owner,details={}))
    with pytest.raises(StaleCaseWriteError):
        repo.save_case(b)
    assert all(e.event_type!='REJECTED_STALE' for e in repo.get_case(cid).events)

def test_reopen_retains_committed_case_and_event(setup):
    repo,svc,cid,owner,url=setup
    case=repo.get_case(cid)
    case.record_event(CaseEvent(event_type='COMMITTED',actor_id=owner,details={}))
    repo.save_case(case)
    fresh=SQLAlchemyKernelRepository(url)
    try:
        x=fresh.get_case(cid)
        assert x.version==3
        assert x.events[-1].event_type=='COMMITTED'
    finally:
        fresh.close()

def test_no_event_state_change_is_rejected(setup):
    repo,svc,cid,owner,url=setup
    case=repo.get_case(cid)
    case.status=CaseStatus.ACTIVE
    with pytest.raises(StaleCaseWriteError):
        repo.save_case(case)
    assert repo.get_case(cid).status==CaseStatus.DRAFT

def test_idempotent_equal_version_retry_allowed(setup):
    repo,svc,cid,owner,url=setup
    before=repo.get_case(cid)
    repo.save_case(before)
    after=repo.get_case(cid)
    assert after.version==before.version
    assert len(after.events)==len(before.events)

def test_missing_persisted_history_is_rejected(setup):
    repo,svc,cid,owner,url=setup
    case=repo.get_case(cid)
    case.events=[]
    with pytest.raises(StaleCaseWriteError):
        repo.save_case(case)

def test_legitimate_service_transitions_still_work(setup):
    repo,svc,cid,owner,url=setup
    x=svc.transition_case(case_id=cid,target=CaseStatus.IN_REVIEW,
                          actor_id=owner,reason='Reviewed')
    assert x.status is CaseStatus.IN_REVIEW
    assert x.version==3

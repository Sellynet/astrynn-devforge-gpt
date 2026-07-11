from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request, status

from .config import APISettings
from .container import RuntimeContainer
from .schemas import (
    ApprovalCreateRequest,
    ApprovalResponse,
    CaseCreateRequest,
    CaseResponse,
    HealthResponse,
    ModuleStatus,
    SystemStatusResponse,
    TransitionRequest,
)


health_router = APIRouter(tags=["system"])
api_router = APIRouter(prefix="/api/v1")


_MODULES = (
    ModuleStatus(name="Kernel mínimo", status="COMPLETADO", evidence="PR #10"),
    ModuleStatus(
        name="Aegis Deployment Clearance", status="COMPLETADO", evidence="PR #11"
    ),
    ModuleStatus(
        name="Orbyn Atlas Case + Briefing", status="COMPLETADO", evidence="PR #12"
    ),
    ModuleStatus(
        name="Output Vault + Proof Receipt", status="COMPLETADO", evidence="PR #13"
    ),
    ModuleStatus(
        name="OAAA Agent Blueprint", status="COMPLETADO", evidence="PR #14"
    ),
    ModuleStatus(name="ARIA Test Register", status="COMPLETADO", evidence="PR #16"),
    ModuleStatus(
        name="Vigilance Permissions Layer", status="COMPLETADO", evidence="PR #17"
    ),
    ModuleStatus(name="FastAPI Control API", status="EN_CONSTRUCCION", evidence="Issue #18"),
)


def get_container(request: Request) -> RuntimeContainer:
    return request.app.state.container


def get_settings(request: Request) -> APISettings:
    return request.app.state.settings


@health_router.get("/health", response_model=HealthResponse)
def health(settings: APISettings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="astrynn-control-api",
        version=settings.version,
        environment=settings.environment,
        persistence=settings.persistence_mode,
        external_actions_enabled=False,
    )


@api_router.get(
    "/system/status",
    response_model=SystemStatusResponse,
    tags=["system"],
)
def system_status(
    container: RuntimeContainer = Depends(get_container),
    settings: APISettings = Depends(get_settings),
) -> SystemStatusResponse:
    return SystemStatusResponse(
        service="astrynn-control-api",
        version=settings.version,
        persistence=settings.persistence_mode,
        modules=list(_MODULES),
        counts=container.counts(),
        external_actions_enabled=False,
    )


@api_router.post(
    "/kernel/cases",
    response_model=CaseResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["kernel"],
)
def create_case(
    payload: CaseCreateRequest,
    container: RuntimeContainer = Depends(get_container),
) -> CaseResponse:
    case = container.kernel_service.create_case(
        title=payload.title,
        description=payload.description,
        owner_id=payload.owner_id,
        organization_id=payload.organization_id,
        sensitivity=payload.sensitivity,
        actor_id=payload.actor_id,
    )
    return CaseResponse.from_domain(case)


@api_router.get(
    "/kernel/cases",
    response_model=list[CaseResponse],
    tags=["kernel"],
)
def list_cases(
    container: RuntimeContainer = Depends(get_container),
) -> list[CaseResponse]:
    cases = sorted(
        container.kernel_repository.list_cases(),
        key=lambda item: item.created_at,
    )
    return [CaseResponse.from_domain(case) for case in cases]


@api_router.get(
    "/kernel/cases/{case_id}",
    response_model=CaseResponse,
    tags=["kernel"],
)
def get_case(
    case_id: UUID,
    container: RuntimeContainer = Depends(get_container),
) -> CaseResponse:
    return CaseResponse.from_domain(container.kernel_repository.get_case(case_id))


@api_router.post(
    "/kernel/cases/{case_id}/approvals",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["kernel"],
)
def record_approval(
    case_id: UUID,
    payload: ApprovalCreateRequest,
    container: RuntimeContainer = Depends(get_container),
) -> ApprovalResponse:
    approval = container.kernel_service.record_approval(
        case_id=case_id,
        approver_id=payload.approver_id,
        decision=payload.decision,
        rationale=payload.rationale,
        conditions=payload.conditions,
    )
    return ApprovalResponse.from_domain(approval)


@api_router.post(
    "/kernel/cases/{case_id}/transitions",
    response_model=CaseResponse,
    tags=["kernel"],
)
def transition_case(
    case_id: UUID,
    payload: TransitionRequest,
    container: RuntimeContainer = Depends(get_container),
) -> CaseResponse:
    case = container.kernel_service.transition_case(
        case_id=case_id,
        target=payload.target,
        actor_id=payload.actor_id,
        reason=payload.reason,
    )
    return CaseResponse.from_domain(case)

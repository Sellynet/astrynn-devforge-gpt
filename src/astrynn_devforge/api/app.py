from __future__ import annotations

from uuid import UUID

from fastapi import FastAPI, HTTPException, status

from astrynn_devforge.kernel import (
    ApprovalRequiredError,
    CaseNotFoundError,
    CaseStatus,
    InvalidTransitionError,
)

from .aegis_routes import router as aegis_router
from .auth import (
    AuthRole,
    CurrentPrincipal,
    Permission,
    Principal,
    require_organization_access,
    require_permission,
)
from .container import ApplicationContainer, build_container
from .schemas import (
    ApprovalCreateRequest,
    ApprovalResponse,
    CaseCreateRequest,
    CaseResponse,
    CaseTransitionRequest,
    HealthResponse,
    PrincipalResponse,
)


def _case_response(case) -> CaseResponse:
    return CaseResponse(
        id=case.id,
        title=case.title,
        description=case.description,
        owner_id=case.owner_id,
        organization_id=case.organization_id,
        sensitivity=case.sensitivity,
        status=case.status,
        created_at=case.created_at,
        updated_at=case.updated_at,
        events=tuple(
            {
                "event_type": event.event_type,
                "actor_id": event.actor_id,
                "details": event.details,
                "created_at": event.created_at,
            }
            for event in case.events
        ),
    )


def _load_case(
    app: FastAPI,
    case_id: UUID,
    principal: Principal,
    permission: Permission,
):
    require_permission(principal, permission)
    try:
        case = app.state.container.kernel_repository.get_case(case_id)
    except CaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc

    require_organization_access(principal, case.organization_id)
    if principal.role is AuthRole.CASE_OWNER and case.owner_id != principal.actor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Case owners may access only their own cases",
        )
    return case


def _assert_owner_transition(principal: Principal, case, target: CaseStatus) -> None:
    if principal.role is not AuthRole.CASE_OWNER:
        return
    if case.owner_id != principal.actor_id:
        raise HTTPException(status_code=403, detail="Case ownership required")
    if target not in {CaseStatus.IN_REVIEW, CaseStatus.CLOSED}:
        raise HTTPException(
            status_code=403,
            detail="Case owners may only submit a draft for review or close it",
        )


def create_app(container: ApplicationContainer | None = None) -> FastAPI:
    app = FastAPI(
        title="Orbyn Atlas + Aegis Private API",
        version="0.4.0",
        description=(
            "Controlled development API with bearer authentication, organization-scoped "
            "RBAC, configurable persistence, and governed Aegis Clearance evaluation. "
            "No external actions or runtime deployment."
        ),
    )
    app.state.container = container or build_container()
    app.include_router(aegis_router)

    @app.get("/health", response_model=HealthResponse, tags=["system"])
    def health() -> HealthResponse:
        return HealthResponse(
            persistence=app.state.container.kernel_repository.persistence_name
        )

    @app.get("/api/v1/me", response_model=PrincipalResponse, tags=["identity"])
    def me(principal: CurrentPrincipal) -> PrincipalResponse:
        return PrincipalResponse(
            actor_id=principal.actor_id,
            organization_id=principal.organization_id,
            role=principal.role,
            display_name=principal.display_name,
        )

    @app.post("/api/v1/cases", response_model=CaseResponse, status_code=201, tags=["kernel"])
    def create_case(payload: CaseCreateRequest, principal: CurrentPrincipal) -> CaseResponse:
        require_permission(principal, Permission.CASE_CREATE)
        require_organization_access(principal, payload.organization_id)
        try:
            case = app.state.container.kernel_service.create_case(
                title=payload.title,
                description=payload.description,
                owner_id=principal.actor_id,
                organization_id=payload.organization_id,
                sensitivity=payload.sensitivity,
                actor_id=principal.actor_id,
            )
            return _case_response(case)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/api/v1/cases", response_model=list[CaseResponse], tags=["kernel"])
    def list_cases(principal: CurrentPrincipal) -> list[CaseResponse]:
        require_permission(principal, Permission.CASE_LIST)
        cases = app.state.container.kernel_repository.list_cases()
        if not principal.is_system_admin:
            cases = [
                case
                for case in cases
                if case.organization_id == principal.organization_id
            ]
        if principal.role is AuthRole.CASE_OWNER:
            cases = [case for case in cases if case.owner_id == principal.actor_id]
        return [_case_response(case) for case in cases]

    @app.get("/api/v1/cases/{case_id}", response_model=CaseResponse, tags=["kernel"])
    def get_case(case_id: UUID, principal: CurrentPrincipal) -> CaseResponse:
        case = _load_case(app, case_id, principal, Permission.CASE_READ)
        return _case_response(case)

    @app.post(
        "/api/v1/cases/{case_id}/transition",
        response_model=CaseResponse,
        tags=["kernel"],
    )
    def transition_case(
        case_id: UUID,
        payload: CaseTransitionRequest,
        principal: CurrentPrincipal,
    ) -> CaseResponse:
        case = _load_case(app, case_id, principal, Permission.CASE_TRANSITION)
        _assert_owner_transition(principal, case, payload.target)
        try:
            transitioned = app.state.container.kernel_service.transition_case(
                case_id=case_id,
                target=payload.target,
                actor_id=principal.actor_id,
                reason=payload.reason,
            )
            return _case_response(transitioned)
        except ApprovalRequiredError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except InvalidTransitionError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.post(
        "/api/v1/cases/{case_id}/approvals",
        response_model=ApprovalResponse,
        status_code=201,
        tags=["kernel"],
    )
    def record_approval(
        case_id: UUID,
        payload: ApprovalCreateRequest,
        principal: CurrentPrincipal,
    ) -> ApprovalResponse:
        case = _load_case(app, case_id, principal, Permission.CASE_APPROVE)
        if case.owner_id == principal.actor_id:
            raise HTTPException(
                status_code=403,
                detail="An actor cannot approve a case they own",
            )
        try:
            approval = app.state.container.kernel_service.record_approval(
                case_id=case_id,
                approver_id=principal.actor_id,
                decision=payload.decision,
                rationale=payload.rationale,
                conditions=payload.conditions,
            )
            return ApprovalResponse(
                id=approval.id,
                case_id=approval.case_id,
                approver_id=approval.approver_id,
                decision=approval.decision,
                rationale=approval.rationale,
                conditions=approval.conditions,
                created_at=approval.created_at,
            )
        except CaseNotFoundError as exc:
            raise HTTPException(status_code=404, detail="Case not found") from exc
        except ApprovalRequiredError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    return app


app = create_app()

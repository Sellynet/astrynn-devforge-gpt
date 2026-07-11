from __future__ import annotations

from uuid import UUID

from fastapi import FastAPI, HTTPException

from astrynn_devforge.kernel import (
    ApprovalRequiredError,
    CaseNotFoundError,
    InvalidTransitionError,
)

from .container import ApplicationContainer, build_container
from .schemas import (
    ApprovalCreateRequest,
    ApprovalResponse,
    CaseCreateRequest,
    CaseResponse,
    CaseTransitionRequest,
    HealthResponse,
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


def create_app(container: ApplicationContainer | None = None) -> FastAPI:
    app = FastAPI(
        title="Orbyn Atlas + Aegis Private API",
        version="0.1.0",
        description="Controlled development API. No external actions or runtime deployment.",
    )
    app.state.container = container or build_container()

    @app.get("/health", response_model=HealthResponse, tags=["system"])
    def health() -> HealthResponse:
        return HealthResponse()

    @app.post("/api/v1/cases", response_model=CaseResponse, status_code=201, tags=["kernel"])
    def create_case(payload: CaseCreateRequest) -> CaseResponse:
        try:
            case = app.state.container.kernel_service.create_case(**payload.model_dump())
            return _case_response(case)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/api/v1/cases", response_model=list[CaseResponse], tags=["kernel"])
    def list_cases() -> list[CaseResponse]:
        cases = app.state.container.kernel_repository.list_cases()
        return [_case_response(case) for case in cases]

    @app.get("/api/v1/cases/{case_id}", response_model=CaseResponse, tags=["kernel"])
    def get_case(case_id: UUID) -> CaseResponse:
        try:
            return _case_response(app.state.container.kernel_repository.get_case(case_id))
        except CaseNotFoundError as exc:
            raise HTTPException(status_code=404, detail="Case not found") from exc

    @app.post(
        "/api/v1/cases/{case_id}/transition",
        response_model=CaseResponse,
        tags=["kernel"],
    )
    def transition_case(case_id: UUID, payload: CaseTransitionRequest) -> CaseResponse:
        try:
            case = app.state.container.kernel_service.transition_case(
                case_id=case_id,
                **payload.model_dump(),
            )
            return _case_response(case)
        except CaseNotFoundError as exc:
            raise HTTPException(status_code=404, detail="Case not found") from exc
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
    def record_approval(case_id: UUID, payload: ApprovalCreateRequest) -> ApprovalResponse:
        try:
            approval = app.state.container.kernel_service.record_approval(
                case_id=case_id,
                **payload.model_dump(),
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

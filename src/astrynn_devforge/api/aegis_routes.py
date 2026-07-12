from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status

from astrynn_devforge.aegis import AIUseCase, AegisClearanceService, RiskScores
from astrynn_devforge.kernel import CaseNotFoundError

from .aegis_schemas import (
    AegisClearanceRequest,
    ClearancePackageResponse,
    RecordedClearanceResponse,
)
from .auth import (
    AuthRole,
    CurrentPrincipal,
    Permission,
    Principal,
    require_organization_access,
    require_permission,
)


router = APIRouter(prefix="/api/v1/aegis", tags=["aegis"])
_service = AegisClearanceService()


def _load_case(
    request: Request,
    case_id: UUID,
    principal: Principal,
    permission: Permission,
):
    require_permission(principal, permission)
    try:
        case = request.app.state.container.kernel_repository.get_case(case_id)
    except CaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc

    require_organization_access(principal, case.organization_id)
    if principal.role is AuthRole.CASE_OWNER and case.owner_id != principal.actor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Case owners may evaluate only their own cases",
        )
    return case


def _build_use_case(case, payload: AegisClearanceRequest) -> AIUseCase:
    return AIUseCase(
        case_id=case.id,
        organization_id=case.organization_id,
        owner_id=case.owner_id,
        title=payload.title,
        purpose=payload.purpose,
        sector=payload.sector,
        scores=RiskScores(**payload.scores.model_dump()),
        data_categories=payload.data_categories,
        systems=payload.systems,
        users=payload.users,
        requested_actions=payload.requested_actions,
        providers=payload.providers,
        specialist_triggers=payload.specialist_triggers,
        critical_blockers=payload.critical_blockers,
    )


def _package_response(package) -> ClearancePackageResponse:
    return ClearancePackageResponse(
        result=package.result.to_dict(),
        receipt=package.receipt.to_dict(),
    )


@router.post(
    "/cases/{case_id}/clearance/evaluate",
    response_model=ClearancePackageResponse,
)
def evaluate_clearance(
    case_id: UUID,
    payload: AegisClearanceRequest,
    request: Request,
    principal: CurrentPrincipal,
) -> ClearancePackageResponse:
    case = _load_case(request, case_id, principal, Permission.AEGIS_EVALUATE)
    try:
        package = _service.evaluate(_build_use_case(case, payload))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _package_response(package)


@router.post(
    "/cases/{case_id}/clearance/record",
    response_model=RecordedClearanceResponse,
    status_code=201,
)
def evaluate_and_record_clearance(
    case_id: UUID,
    payload: AegisClearanceRequest,
    request: Request,
    principal: CurrentPrincipal,
) -> RecordedClearanceResponse:
    case = _load_case(request, case_id, principal, Permission.AEGIS_RECORD)
    if case.owner_id == principal.actor_id:
        raise HTTPException(
            status_code=403,
            detail="A case owner cannot record the final clearance evidence",
        )
    try:
        package = _service.evaluate(_build_use_case(case, payload))
        output, evidence = _service.record(
            package=package,
            repository=request.app.state.container.kernel_repository,
            owner_id=principal.actor_id,
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return RecordedClearanceResponse(
        package=_package_response(package),
        output_id=output.id,
        evidence_id=evidence.id,
        artifact_status=output.status.value,
    )

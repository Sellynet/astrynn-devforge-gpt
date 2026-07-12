from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status

from astrynn_devforge.atlas import (
    AtlasCaseInput,
    AtlasRisk,
    AtlasScenario,
    AtlasSignal,
    AtlasSource,
    AtlasStakeholder,
    AtlasValidationError,
    OrbynAtlasService,
)
from astrynn_devforge.kernel import CaseNotFoundError

from .atlas_schemas import (
    AtlasBriefingRequest,
    AtlasPackageResponse,
    RecordedAtlasBriefingResponse,
)
from .auth import (
    AuthRole,
    CurrentPrincipal,
    Permission,
    Principal,
    require_organization_access,
    require_permission,
)


router = APIRouter(prefix="/api/v1/atlas", tags=["atlas"])


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
            detail="Case owners may build Atlas briefings only for their own cases",
        )
    return case


def _build_package(request: Request, case, payload: AtlasBriefingRequest):
    service = OrbynAtlasService(request.app.state.container.kernel_repository)
    case_input = AtlasCaseInput(
        case_id=case.id,
        organization_id=case.organization_id,
        owner_id=case.owner_id,
        title=payload.case_input.title,
        problem=payload.case_input.problem,
        sector=payload.case_input.sector,
        country=payload.case_input.country,
        horizon_days=payload.case_input.horizon_days,
        asset=payload.case_input.asset,
    )
    sources = tuple(
        AtlasSource(
            id=item.id,
            case_id=case.id,
            title=item.title,
            kind=item.kind,
            confidence=item.confidence,
            sensitivity=item.sensitivity,
            uri=item.uri,
            notes=item.notes,
        )
        for item in payload.sources
    )
    signals = tuple(
        AtlasSignal(
            id=item.id,
            case_id=case.id,
            title=item.title,
            observation=item.observation,
            source_ids=item.source_ids,
            confidence=item.confidence,
        )
        for item in payload.signals
    )
    risks = tuple(
        AtlasRisk(
            id=item.id,
            case_id=case.id,
            title=item.title,
            description=item.description,
            probability=item.probability,
            impact=item.impact,
            related_signal_ids=item.related_signal_ids,
            mitigation=item.mitigation,
        )
        for item in payload.risks
    )
    stakeholders = tuple(
        AtlasStakeholder(
            id=item.id,
            case_id=case.id,
            name=item.name,
            role=item.role,
            influence=item.influence,
            exposure=item.exposure,
            interests=item.interests,
        )
        for item in payload.stakeholders
    )
    scenarios = tuple(
        AtlasScenario(
            id=item.id,
            case_id=case.id,
            scenario_type=item.scenario_type,
            title=item.title,
            narrative=item.narrative,
            assumptions=item.assumptions,
            early_indicators=item.early_indicators,
            response_options=item.response_options,
        )
        for item in payload.scenarios
    )
    package = service.build_package(
        case_input=case_input,
        sources=sources,
        signals=signals,
        risks=risks,
        stakeholders=stakeholders,
        scenarios=scenarios,
    )
    return service, package


def _package_response(package) -> AtlasPackageResponse:
    return AtlasPackageResponse(
        briefing=package.briefing.to_dict(),
        receipt=package.receipt.to_dict(),
    )


@router.post(
    "/cases/{case_id}/briefing/build",
    response_model=AtlasPackageResponse,
)
def build_briefing(
    case_id: UUID,
    payload: AtlasBriefingRequest,
    request: Request,
    principal: CurrentPrincipal,
) -> AtlasPackageResponse:
    case = _load_case(request, case_id, principal, Permission.ATLAS_BUILD)
    try:
        _, package = _build_package(request, case, payload)
    except (AtlasValidationError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _package_response(package)


@router.post(
    "/cases/{case_id}/briefing/record",
    response_model=RecordedAtlasBriefingResponse,
    status_code=201,
)
def build_and_record_briefing(
    case_id: UUID,
    payload: AtlasBriefingRequest,
    request: Request,
    principal: CurrentPrincipal,
) -> RecordedAtlasBriefingResponse:
    case = _load_case(request, case_id, principal, Permission.ATLAS_RECORD)
    if case.owner_id == principal.actor_id:
        raise HTTPException(
            status_code=403,
            detail="A case owner cannot record the final Atlas briefing evidence",
        )
    try:
        service, package = _build_package(request, case, payload)
        output, evidence = service.record_package(
            package=package,
            owner_id=principal.actor_id,
            sensitivity=case.sensitivity,
        )
    except (AtlasValidationError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return RecordedAtlasBriefingResponse(
        package=_package_response(package),
        output_id=output.id,
        evidence_id=evidence.id,
        artifact_status=output.status.value,
    )

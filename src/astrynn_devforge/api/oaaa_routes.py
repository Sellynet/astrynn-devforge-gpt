from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status

from astrynn_devforge.kernel import CaseNotFoundError
from astrynn_devforge.oaaa import (
    ApprovalPoint,
    ARIATestRequirement,
    BlueprintApprovalError,
    BlueprintNotFoundError,
    BlueprintTransitionError,
    DataBoundary,
    ToolPermission,
)

from .auth import (
    AuthRole,
    CurrentPrincipal,
    Permission,
    Principal,
    require_organization_access,
    require_permission,
)
from .oaaa_schemas import (
    OAAABlueprintDefinitionRequest,
    OAAABlueprintHistoryResponse,
    OAAABlueprintResponse,
    OAAABlueprintRevisionRequest,
    OAAABlueprintSubmitRequest,
)

router = APIRouter(prefix="/api/v1/oaaa", tags=["oaaa"])


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
            detail="Case owners may design OAAA blueprints only for their own cases",
        )
    return case


def _load_blueprint(
    request: Request,
    blueprint_id: UUID,
    principal: Principal,
    permission: Permission,
):
    require_permission(principal, permission)
    try:
        blueprint = request.app.state.container.blueprint_repository.latest_version(
            blueprint_id
        )
    except BlueprintNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Blueprint not found") from exc

    require_organization_access(principal, blueprint.organization_id)
    if principal.role is AuthRole.CASE_OWNER and blueprint.owner_id != principal.actor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Case owners may access only blueprints for their own cases",
        )
    return blueprint


def _definition_kwargs(payload: OAAABlueprintDefinitionRequest) -> dict[str, object]:
    return {
        "name": payload.name,
        "business_need": payload.business_need,
        "role": payload.role,
        "objective": payload.objective,
        "tools": tuple(
            ToolPermission(
                name=item.name,
                allowed_operations=item.allowed_operations,
                prohibited_operations=item.prohibited_operations,
                requires_human_approval=item.requires_human_approval,
            )
            for item in payload.tools
        ),
        "data_boundary": DataBoundary(
            allowed_categories=payload.data_boundary.allowed_categories,
            prohibited_categories=payload.data_boundary.prohibited_categories,
            retention_rule=payload.data_boundary.retention_rule,
            deletion_rule=payload.data_boundary.deletion_rule,
        ),
        "allowed_actions": payload.allowed_actions,
        "prohibited_actions": payload.prohibited_actions,
        "autonomy_level": payload.autonomy_level,
        "approval_points": tuple(
            ApprovalPoint(
                trigger=item.trigger,
                approver_role=item.approver_role,
                action_if_unavailable=item.action_if_unavailable,
            )
            for item in payload.approval_points
        ),
        "logs_required": payload.logs_required,
        "aria_test_plan": tuple(
            ARIATestRequirement(
                family=item.family,
                objective=item.objective,
                pass_criteria=item.pass_criteria,
            )
            for item in payload.aria_test_plan
        ),
        "rollback_procedure": payload.rollback_procedure,
        "disable_procedure": payload.disable_procedure,
    }


def _response(blueprint) -> OAAABlueprintResponse:
    return OAAABlueprintResponse(blueprint=blueprint.to_dict())


@router.post(
    "/cases/{case_id}/blueprints",
    response_model=OAAABlueprintResponse,
    status_code=201,
)
def create_blueprint(
    case_id: UUID,
    payload: OAAABlueprintDefinitionRequest,
    request: Request,
    principal: CurrentPrincipal,
) -> OAAABlueprintResponse:
    case = _load_case(request, case_id, principal, Permission.OAAA_CREATE)
    try:
        blueprint = request.app.state.container.oaaa_service.create_draft(
            case_id=case.id,
            organization_id=case.organization_id,
            owner_id=case.owner_id,
            created_by=principal.actor_id,
            sensitivity=case.sensitivity,
            **_definition_kwargs(payload),
        )
    except (BlueprintApprovalError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _response(blueprint)


@router.get(
    "/blueprints/{blueprint_id}",
    response_model=OAAABlueprintResponse,
)
def get_latest_blueprint(
    blueprint_id: UUID,
    request: Request,
    principal: CurrentPrincipal,
) -> OAAABlueprintResponse:
    blueprint = _load_blueprint(request, blueprint_id, principal, Permission.OAAA_READ)
    return _response(blueprint)


@router.get(
    "/blueprints/{blueprint_id}/versions",
    response_model=OAAABlueprintHistoryResponse,
)
def get_blueprint_history(
    blueprint_id: UUID,
    request: Request,
    principal: CurrentPrincipal,
) -> OAAABlueprintHistoryResponse:
    _load_blueprint(request, blueprint_id, principal, Permission.OAAA_READ)
    versions = request.app.state.container.blueprint_repository.versions_for_blueprint(
        blueprint_id
    )
    return OAAABlueprintHistoryResponse(
        blueprint_id=blueprint_id,
        versions=tuple(version.to_dict() for version in versions),
    )


@router.post(
    "/blueprints/{blueprint_id}/revisions",
    response_model=OAAABlueprintResponse,
    status_code=201,
)
def revise_blueprint(
    blueprint_id: UUID,
    payload: OAAABlueprintRevisionRequest,
    request: Request,
    principal: CurrentPrincipal,
) -> OAAABlueprintResponse:
    _load_blueprint(request, blueprint_id, principal, Permission.OAAA_REVISE)
    try:
        blueprint = request.app.state.container.oaaa_service.revise(
            blueprint_id=blueprint_id,
            created_by=principal.actor_id,
            change_summary=payload.change_summary,
            **_definition_kwargs(payload),
        )
    except BlueprintTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except (BlueprintApprovalError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _response(blueprint)


@router.post(
    "/blueprints/{blueprint_id}/submit",
    response_model=OAAABlueprintResponse,
)
def submit_blueprint(
    blueprint_id: UUID,
    payload: OAAABlueprintSubmitRequest,
    request: Request,
    principal: CurrentPrincipal,
) -> OAAABlueprintResponse:
    _load_blueprint(request, blueprint_id, principal, Permission.OAAA_SUBMIT)
    try:
        blueprint = request.app.state.container.oaaa_service.submit_for_review(
            blueprint_id=blueprint_id,
            submitted_by=principal.actor_id,
            reason=payload.reason,
        )
    except BlueprintTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except (BlueprintApprovalError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _response(blueprint)

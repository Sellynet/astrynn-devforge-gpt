from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import Field

from astrynn_devforge.oaaa import ARIATestFamily, AutonomyLevel

from .schemas import APIModel


class OAAAToolPermissionRequest(APIModel):
    name: str = Field(min_length=1, max_length=200)
    allowed_operations: tuple[str, ...] = Field(min_length=1)
    prohibited_operations: tuple[str, ...] = ()
    requires_human_approval: bool = True


class OAAADataBoundaryRequest(APIModel):
    allowed_categories: tuple[str, ...] = Field(min_length=1)
    prohibited_categories: tuple[str, ...] = Field(min_length=1)
    retention_rule: str = Field(min_length=1, max_length=2000)
    deletion_rule: str = Field(min_length=1, max_length=2000)


class OAAAApprovalPointRequest(APIModel):
    trigger: str = Field(min_length=1, max_length=1000)
    approver_role: str = Field(min_length=1, max_length=200)
    action_if_unavailable: str = Field(default="STOP", min_length=1, max_length=500)


class OAAAARIATestRequirementRequest(APIModel):
    family: ARIATestFamily
    objective: str = Field(min_length=1, max_length=2000)
    pass_criteria: str = Field(min_length=1, max_length=2000)


class OAAABlueprintDefinitionRequest(APIModel):
    name: str = Field(min_length=1, max_length=200)
    business_need: str = Field(min_length=1, max_length=3000)
    role: str = Field(min_length=1, max_length=1000)
    objective: str = Field(min_length=1, max_length=3000)
    tools: tuple[OAAAToolPermissionRequest, ...] = Field(min_length=1)
    data_boundary: OAAADataBoundaryRequest
    allowed_actions: tuple[str, ...] = Field(min_length=1)
    prohibited_actions: tuple[str, ...] = Field(min_length=1)
    autonomy_level: AutonomyLevel
    approval_points: tuple[OAAAApprovalPointRequest, ...] = Field(min_length=1)
    logs_required: tuple[str, ...] = Field(min_length=1)
    aria_test_plan: tuple[OAAAARIATestRequirementRequest, ...] = Field(min_length=1)
    rollback_procedure: str = Field(min_length=1, max_length=5000)
    disable_procedure: str = Field(min_length=1, max_length=5000)


class OAAABlueprintRevisionRequest(OAAABlueprintDefinitionRequest):
    change_summary: str = Field(min_length=1, max_length=2000)


class OAAABlueprintSubmitRequest(APIModel):
    reason: str = Field(
        default="Submitted for governed OAAA review",
        min_length=1,
        max_length=2000,
    )


class OAAABlueprintResponse(APIModel):
    blueprint: dict[str, Any]
    control_plane_persistence: str = "in-memory-development"


class OAAABlueprintHistoryResponse(APIModel):
    blueprint_id: UUID
    versions: tuple[dict[str, Any], ...]
    control_plane_persistence: str = "in-memory-development"

from pathlib import Path
from uuid import UUID, uuid4

from astrynn_devforge.aegis import ClearanceDecision
from astrynn_devforge.kernel import Sensitivity
from astrynn_devforge.oaaa import (
    ApprovalPoint,
    ARIATestFamily,
    ARIATestRequirement,
    AutonomyLevel,
    BlueprintStatus,
    DataBoundary,
    HumanDecision,
    ToolPermission,
)
from astrynn_devforge.oaaa.models import (
    ActivationReceipt,
    AgentBlueprintVersion,
    HumanApprovalRecord,
)
from astrynn_devforge.persistence import SQLAlchemyAgentBlueprintRepository


def build_blueprint(
    *,
    blueprint_id: UUID | None = None,
    version: int = 1,
    parent_version_id: UUID | None = None,
) -> AgentBlueprintVersion:
    return AgentBlueprintVersion(
        blueprint_id=blueprint_id or uuid4(),
        case_id=uuid4(),
        organization_id=uuid4(),
        owner_id=uuid4(),
        created_by=uuid4(),
        name="Persistent Customer Evidence Assistant",
        business_need="Preserve governed agent design across application restarts",
        role="Prepare reviewable customer response drafts",
        objective="Produce evidence-linked drafts without autonomous sending",
        tools=(
            ToolPermission(
                name="gmail_draft",
                allowed_operations=("read_approved_thread", "create_draft"),
                prohibited_operations=("send", "delete"),
                requires_human_approval=True,
            ),
        ),
        data_boundary=DataBoundary(
            allowed_categories=("approved customer messages",),
            prohibited_categories=("credentials", "health data", "payment data"),
            retention_rule="Retain working context for no more than 30 days",
            deletion_rule="Delete working context on case closure or owner request",
        ),
        allowed_actions=("read approved thread", "create response draft"),
        prohibited_actions=(
            "send email",
            "delete email",
            "change permissions",
            "deploy itself",
        ),
        autonomy_level=AutonomyLevel.APPROVAL_GATED,
        approval_points=(
            ApprovalPoint(
                trigger="Before any external communication",
                approver_role="Named account owner",
            ),
        ),
        logs_required=(
            "input source IDs",
            "tool calls",
            "draft versions",
            "human decisions",
        ),
        aria_test_plan=(
            ARIATestRequirement(
                family=ARIATestFamily.PROMPT_INJECTION,
                objective="Reject hidden instructions in customer content",
                pass_criteria="No hidden instruction changes role or permissions",
            ),
            ARIATestRequirement(
                family=ARIATestFamily.TOOL_PERMISSION_DRIFT,
                objective="Prevent unapproved send or delete operations",
                pass_criteria="Only explicitly allowed draft operations are requested",
            ),
            ARIATestRequirement(
                family=ARIATestFamily.INCIDENT_TRIGGER,
                objective="Stop and escalate on prohibited data or action requests",
                pass_criteria="Agent stops, logs and routes the event to the owner",
            ),
        ),
        rollback_procedure="Restore the last approved prompt and tool allow-list",
        disable_procedure="Revoke tool token and set the blueprint to SUSPENDED",
        sensitivity=Sensitivity.GREEN,
        version=version,
        status=BlueprintStatus.DRAFT,
        material_change=True,
        parent_version_id=parent_version_id,
        change_summary="Initial persistent OAAA blueprint",
        status_reason="Awaiting governed review",
    )


def test_sqlalchemy_oaaa_repository_survives_restart(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'oaaa.db'}"

    repository_a = SQLAlchemyAgentBlueprintRepository(
        database_url,
        create_schema=True,
    )
    original = build_blueprint()
    stored = repository_a.append_version(original)
    repository_a.close()

    repository_b = SQLAlchemyAgentBlueprintRepository(database_url)
    recovered = repository_b.latest_version(original.blueprint_id)
    history = repository_b.versions_for_blueprint(original.blueprint_id)
    repository_b.close()

    assert recovered == stored
    assert recovered.to_dict() == original.to_dict()
    assert history == (stored,)



def test_sqlalchemy_oaaa_approval_survives_restart(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'oaaa-approval.db'}"

    repository_a = SQLAlchemyAgentBlueprintRepository(
        database_url,
        create_schema=True,
    )
    blueprint = repository_a.append_version(build_blueprint())
    approval = HumanApprovalRecord(
        blueprint_id=blueprint.blueprint_id,
        blueprint_version_id=blueprint.id,
        blueprint_fingerprint=blueprint.safety_fingerprint,
        approver_id=uuid4(),
        decision=HumanDecision.APPROVE,
        rationale="Named human approval for persistent OAAA test",
        clearance_result_id=uuid4(),
        vault_receipt_id=uuid4(),
        vault_receipt_hash="a" * 64,
    )
    stored = repository_a.append_approval(approval)
    repository_a.close()

    repository_b = SQLAlchemyAgentBlueprintRepository(database_url)
    recovered = repository_b.approvals_for_blueprint(
        blueprint.blueprint_id
    )
    repository_b.close()

    assert recovered == (stored,)



def test_sqlalchemy_oaaa_activation_receipt_survives_restart(
    tmp_path: Path,
) -> None:
    database_url = f"sqlite:///{tmp_path / 'oaaa-activation.db'}"

    repository_a = SQLAlchemyAgentBlueprintRepository(
        database_url,
        create_schema=True,
    )
    blueprint = repository_a.append_version(build_blueprint())
    receipt = ActivationReceipt(
        blueprint_id=blueprint.blueprint_id,
        blueprint_version_id=blueprint.id,
        blueprint_fingerprint=blueprint.safety_fingerprint,
        clearance_result_id=uuid4(),
        clearance_decision=ClearanceDecision.APTO,
        human_approval_id=uuid4(),
        activated_by=uuid4(),
        activation_note=(
            "Governance activation recorded for persistence test"
        ),
        vault_receipt_id=uuid4(),
        vault_receipt_hash="b" * 64,
    )
    stored = repository_a.append_activation_receipt(receipt)
    repository_a.close()

    repository_b = SQLAlchemyAgentBlueprintRepository(database_url)
    recovered = repository_b.activation_receipts_for_blueprint(
        blueprint.blueprint_id
    )
    repository_b.close()

    assert recovered == (stored,)

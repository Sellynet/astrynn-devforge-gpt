from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    select,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool

from astrynn_devforge.aegis import ClearanceDecision
from astrynn_devforge.kernel import Sensitivity
from astrynn_devforge.oaaa.enums import (
    ARIATestFamily,
    AutonomyLevel,
    BlueprintStatus,
    HumanDecision,
)
from astrynn_devforge.oaaa.models import (
    ActivationReceipt,
    AgentBlueprintVersion,
    ApprovalPoint,
    ARIATestRequirement,
    DataBoundary,
    HumanApprovalRecord,
    ToolPermission,
)
from astrynn_devforge.oaaa.repository import (
    BlueprintNotFoundError,
    DuplicateBlueprintVersionError,
)


class OAAABase(DeclarativeBase):
    pass


class AgentBlueprintVersionRow(OAAABase):
    __tablename__ = "oaaa_blueprint_versions"
    __table_args__ = (
        UniqueConstraint(
            "blueprint_id",
            "version",
            name="uq_oaaa_blueprint_version",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    blueprint_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_version_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class HumanApprovalRow(OAAABase):
    __tablename__ = "oaaa_human_approvals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    blueprint_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )
    blueprint_version_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("oaaa_blueprint_versions.id"),
        nullable=False,
        index=True,
    )
    blueprint_fingerprint: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    approver_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )
    decision: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )
    rationale: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    conditions: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    clearance_result_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )
    vault_receipt_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )
    vault_receipt_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class ActivationReceiptRow(OAAABase):
    __tablename__ = "oaaa_activation_receipts"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )
    blueprint_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )
    blueprint_version_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("oaaa_blueprint_versions.id"),
        nullable=False,
        index=True,
    )
    blueprint_fingerprint: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    clearance_result_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )
    clearance_decision: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )
    human_approval_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )
    activated_by: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )
    activation_note: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    vault_receipt_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )
    vault_receipt_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    methodology_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


def _aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _build_engine(database_url: str) -> Engine:
    kwargs: dict[str, Any] = {"future": True}

    if database_url in {"sqlite://", "sqlite:///:memory:"}:
        kwargs["connect_args"] = {"check_same_thread": False}
        kwargs["poolclass"] = StaticPool

    return create_engine(database_url, **kwargs)


def _optional_uuid(value: str | None) -> UUID | None:
    return UUID(value) if value else None


class SQLAlchemyAgentBlueprintRepository:
    """SQL-backed append-only repository for governed OAAA blueprints."""

    def __init__(
        self,
        database_url: str,
        *,
        create_schema: bool = False,
        engine: Engine | None = None,
    ) -> None:
        if not database_url.strip():
            raise ValueError("database_url is required")

        self.engine = engine or _build_engine(database_url)
        self._sessions = sessionmaker(
            bind=self.engine,
            class_=Session,
            expire_on_commit=False,
        )

        if create_schema:
            self.create_schema()

    @property
    def persistence_name(self) -> str:
        return f"sqlalchemy-{self.engine.dialect.name}"

    def create_schema(self) -> None:
        OAAABase.metadata.create_all(self.engine)

    def close(self) -> None:
        self.engine.dispose()

    def append_version(
        self,
        blueprint: AgentBlueprintVersion,
    ) -> AgentBlueprintVersion:
        blueprint_id = str(blueprint.blueprint_id)

        with self._sessions.begin() as session:
            rows = session.scalars(
                select(AgentBlueprintVersionRow)
                .where(AgentBlueprintVersionRow.blueprint_id == blueprint_id)
                .order_by(AgentBlueprintVersionRow.version)
            ).all()

            expected_version = len(rows) + 1
            if blueprint.version != expected_version:
                raise DuplicateBlueprintVersionError(
                    f"Expected blueprint version {expected_version}, "
                    f"got {blueprint.version}"
                )

            if rows and blueprint.parent_version_id != UUID(rows[-1].id):
                raise DuplicateBlueprintVersionError(
                    "A new blueprint version must reference "
                    "the previous version"
                )

            if not rows and blueprint.parent_version_id is not None:
                raise DuplicateBlueprintVersionError(
                    "The first blueprint version cannot have "
                    "a parent version"
                )

            if session.get(AgentBlueprintVersionRow, str(blueprint.id)):
                raise DuplicateBlueprintVersionError(
                    f"Blueprint version ID {blueprint.id} already exists"
                )

            session.add(
                AgentBlueprintVersionRow(
                    id=str(blueprint.id),
                    blueprint_id=blueprint_id,
                    version=blueprint.version,
                    parent_version_id=(
                        str(blueprint.parent_version_id)
                        if blueprint.parent_version_id
                        else None
                    ),
                    payload=blueprint.to_dict(),
                    created_at=blueprint.created_at,
                )
            )

        return self.latest_version(blueprint.blueprint_id)

    def latest_version(
        self,
        blueprint_id: UUID,
    ) -> AgentBlueprintVersion:
        with self._sessions() as session:
            row = session.scalar(
                select(AgentBlueprintVersionRow)
                .where(
                    AgentBlueprintVersionRow.blueprint_id
                    == str(blueprint_id)
                )
                .order_by(AgentBlueprintVersionRow.version.desc())
                .limit(1)
            )

            if row is None:
                raise BlueprintNotFoundError(str(blueprint_id))

            return self._blueprint_from_payload(row.payload)

    def versions_for_blueprint(
        self,
        blueprint_id: UUID,
    ) -> tuple[AgentBlueprintVersion, ...]:
        with self._sessions() as session:
            rows = session.scalars(
                select(AgentBlueprintVersionRow)
                .where(
                    AgentBlueprintVersionRow.blueprint_id
                    == str(blueprint_id)
                )
                .order_by(AgentBlueprintVersionRow.version)
            ).all()

            if not rows:
                raise BlueprintNotFoundError(str(blueprint_id))

            return tuple(
                self._blueprint_from_payload(row.payload)
                for row in rows
            )

    def append_approval(
        self,
        approval: HumanApprovalRecord,
    ) -> HumanApprovalRecord:
        with self._sessions.begin() as session:
            version_row = session.get(
                AgentBlueprintVersionRow,
                str(approval.blueprint_version_id),
            )
            if version_row is None:
                raise BlueprintNotFoundError(
                    str(approval.blueprint_version_id)
                )
            if version_row.blueprint_id != str(approval.blueprint_id):
                raise ValueError(
                    "Approval blueprint_id must match its blueprint version"
                )

            existing = session.get(
                HumanApprovalRow,
                str(approval.id),
            )
            if existing is not None:
                stored = self._approval_from_row(existing)
                if stored != approval:
                    raise ValueError(
                        "Approval ID already exists with different content"
                    )
                return stored

            session.add(
                HumanApprovalRow(
                    id=str(approval.id),
                    blueprint_id=str(approval.blueprint_id),
                    blueprint_version_id=str(
                        approval.blueprint_version_id
                    ),
                    blueprint_fingerprint=(
                        approval.blueprint_fingerprint
                    ),
                    approver_id=str(approval.approver_id),
                    decision=approval.decision.value,
                    rationale=approval.rationale,
                    conditions=list(approval.conditions),
                    clearance_result_id=str(
                        approval.clearance_result_id
                    ),
                    vault_receipt_id=str(
                        approval.vault_receipt_id
                    ),
                    vault_receipt_hash=approval.vault_receipt_hash,
                    created_at=approval.created_at,
                )
            )

        recovered = self.approvals_for_blueprint(
            approval.blueprint_id
        )
        return next(
            item for item in recovered if item.id == approval.id
        )

    def approvals_for_blueprint(
        self,
        blueprint_id: UUID,
    ) -> tuple[HumanApprovalRecord, ...]:
        with self._sessions() as session:
            rows = session.scalars(
                select(HumanApprovalRow)
                .where(
                    HumanApprovalRow.blueprint_id
                    == str(blueprint_id)
                )
                .order_by(
                    HumanApprovalRow.created_at,
                    HumanApprovalRow.id,
                )
            ).all()

            return tuple(
                self._approval_from_row(row)
                for row in rows
            )

    @staticmethod
    def _approval_from_row(
        row: HumanApprovalRow,
    ) -> HumanApprovalRecord:
        return HumanApprovalRecord(
            id=UUID(row.id),
            blueprint_id=UUID(row.blueprint_id),
            blueprint_version_id=UUID(
                row.blueprint_version_id
            ),
            blueprint_fingerprint=row.blueprint_fingerprint,
            approver_id=UUID(row.approver_id),
            decision=HumanDecision(row.decision),
            rationale=row.rationale,
            conditions=tuple(row.conditions or ()),
            clearance_result_id=UUID(
                row.clearance_result_id
            ),
            vault_receipt_id=UUID(row.vault_receipt_id),
            vault_receipt_hash=row.vault_receipt_hash,
            created_at=_aware(row.created_at),
        )

    def append_activation_receipt(
        self,
        receipt: ActivationReceipt,
    ) -> ActivationReceipt:
        with self._sessions.begin() as session:
            version_row = session.get(
                AgentBlueprintVersionRow,
                str(receipt.blueprint_version_id),
            )
            if version_row is None:
                raise BlueprintNotFoundError(
                    str(receipt.blueprint_version_id)
                )

            if version_row.blueprint_id != str(
                receipt.blueprint_id
            ):
                raise ValueError(
                    "Activation receipt blueprint_id must "
                    "match its blueprint version"
                )

            existing = session.get(
                ActivationReceiptRow,
                str(receipt.id),
            )
            if existing is not None:
                stored = self._activation_receipt_from_row(
                    existing
                )
                if stored != receipt:
                    raise ValueError(
                        "Activation receipt ID already exists "
                        "with different content"
                    )
                return stored

            session.add(
                ActivationReceiptRow(
                    id=str(receipt.id),
                    blueprint_id=str(receipt.blueprint_id),
                    blueprint_version_id=str(
                        receipt.blueprint_version_id
                    ),
                    blueprint_fingerprint=(
                        receipt.blueprint_fingerprint
                    ),
                    clearance_result_id=str(
                        receipt.clearance_result_id
                    ),
                    clearance_decision=(
                        receipt.clearance_decision.value
                    ),
                    human_approval_id=str(
                        receipt.human_approval_id
                    ),
                    activated_by=str(receipt.activated_by),
                    activation_note=receipt.activation_note,
                    vault_receipt_id=str(
                        receipt.vault_receipt_id
                    ),
                    vault_receipt_hash=(
                        receipt.vault_receipt_hash
                    ),
                    methodology_version=(
                        receipt.methodology_version
                    ),
                    created_at=receipt.created_at,
                )
            )

        recovered = (
            self.activation_receipts_for_blueprint(
                receipt.blueprint_id
            )
        )
        return next(
            item for item in recovered
            if item.id == receipt.id
        )

    def activation_receipts_for_blueprint(
        self,
        blueprint_id: UUID,
    ) -> tuple[ActivationReceipt, ...]:
        with self._sessions() as session:
            rows = session.scalars(
                select(ActivationReceiptRow)
                .where(
                    ActivationReceiptRow.blueprint_id
                    == str(blueprint_id)
                )
                .order_by(
                    ActivationReceiptRow.created_at,
                    ActivationReceiptRow.id,
                )
            ).all()

            return tuple(
                self._activation_receipt_from_row(row)
                for row in rows
            )

    @staticmethod
    def _activation_receipt_from_row(
        row: ActivationReceiptRow,
    ) -> ActivationReceipt:
        return ActivationReceipt(
            id=UUID(row.id),
            blueprint_id=UUID(row.blueprint_id),
            blueprint_version_id=UUID(
                row.blueprint_version_id
            ),
            blueprint_fingerprint=(
                row.blueprint_fingerprint
            ),
            clearance_result_id=UUID(
                row.clearance_result_id
            ),
            clearance_decision=ClearanceDecision(
                row.clearance_decision
            ),
            human_approval_id=UUID(
                row.human_approval_id
            ),
            activated_by=UUID(row.activated_by),
            activation_note=row.activation_note,
            vault_receipt_id=UUID(
                row.vault_receipt_id
            ),
            vault_receipt_hash=row.vault_receipt_hash,
            methodology_version=(
                row.methodology_version
            ),
            created_at=_aware(row.created_at),
        )

    @staticmethod
    def _blueprint_from_payload(
        payload: dict[str, Any],
    ) -> AgentBlueprintVersion:
        clearance_decision = payload.get("clearance_decision")

        return AgentBlueprintVersion(
            id=UUID(payload["id"]),
            blueprint_id=UUID(payload["blueprint_id"]),
            case_id=UUID(payload["case_id"]),
            organization_id=UUID(payload["organization_id"]),
            owner_id=UUID(payload["owner_id"]),
            created_by=UUID(payload["created_by"]),
            name=payload["name"],
            business_need=payload["business_need"],
            role=payload["role"],
            objective=payload["objective"],
            tools=tuple(
                ToolPermission(
                    name=item["name"],
                    allowed_operations=tuple(
                        item["allowed_operations"]
                    ),
                    prohibited_operations=tuple(
                        item.get("prohibited_operations", ())
                    ),
                    requires_human_approval=item[
                        "requires_human_approval"
                    ],
                )
                for item in payload["tools"]
            ),
            data_boundary=DataBoundary(
                allowed_categories=tuple(
                    payload["data_boundary"]["allowed_categories"]
                ),
                prohibited_categories=tuple(
                    payload["data_boundary"]["prohibited_categories"]
                ),
                retention_rule=payload["data_boundary"][
                    "retention_rule"
                ],
                deletion_rule=payload["data_boundary"][
                    "deletion_rule"
                ],
            ),
            allowed_actions=tuple(payload["allowed_actions"]),
            prohibited_actions=tuple(payload["prohibited_actions"]),
            autonomy_level=AutonomyLevel(
                payload["autonomy_level"]
            ),
            approval_points=tuple(
                ApprovalPoint(
                    trigger=item["trigger"],
                    approver_role=item["approver_role"],
                    action_if_unavailable=item[
                        "action_if_unavailable"
                    ],
                )
                for item in payload["approval_points"]
            ),
            logs_required=tuple(payload["logs_required"]),
            aria_test_plan=tuple(
                ARIATestRequirement(
                    family=ARIATestFamily(item["family"]),
                    objective=item["objective"],
                    pass_criteria=item["pass_criteria"],
                )
                for item in payload["aria_test_plan"]
            ),
            rollback_procedure=payload["rollback_procedure"],
            disable_procedure=payload["disable_procedure"],
            sensitivity=Sensitivity(payload["sensitivity"]),
            version=payload["version"],
            status=BlueprintStatus(payload["status"]),
            material_change=payload["material_change"],
            vault_artifact_id=_optional_uuid(
                payload.get("vault_artifact_id")
            ),
            parent_version_id=_optional_uuid(
                payload.get("parent_version_id")
            ),
            clearance_result_id=_optional_uuid(
                payload.get("clearance_result_id")
            ),
            clearance_decision=(
                ClearanceDecision(clearance_decision)
                if clearance_decision
                else None
            ),
            clearance_conditions=tuple(
                payload.get("clearance_conditions", ())
            ),
            clearance_guardrail_codes=tuple(
                payload.get("clearance_guardrail_codes", ())
            ),
            human_approval_id=_optional_uuid(
                payload.get("human_approval_id")
            ),
            change_summary=payload.get("change_summary", ""),
            status_reason=payload.get("status_reason", ""),
            created_at=_aware(
                datetime.fromisoformat(payload["created_at"])
            ),
        )

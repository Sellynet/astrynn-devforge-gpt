from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool

from astrynn_devforge.kernel import (
    ApprovalDecision,
    ApprovalRecord,
    ArtifactStatus,
    Case,
    CaseEvent,
    CaseNotFoundError,
    CaseStatus,
    EvidenceReference,
    OutputArtifact,
    Sensitivity,
)


class Base(DeclarativeBase):
    pass


class CaseRow(Base):
    __tablename__ = "kernel_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    owner_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    sensitivity: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CaseEventRow(Base):
    __tablename__ = "kernel_case_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("kernel_cases.id"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(36), nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ApprovalRow(Base):
    __tablename__ = "kernel_approvals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("kernel_cases.id"), nullable=False, index=True
    )
    approver_id: Mapped[str] = mapped_column(String(36), nullable=False)
    decision: Mapped[str] = mapped_column(String(40), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    conditions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class EvidenceRow(Base):
    __tablename__ = "kernel_evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("kernel_cases.id"), nullable=False, index=True
    )
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    uri: Mapped[str] = mapped_column(Text, nullable=False)
    sensitivity: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OutputRow(Base):
    __tablename__ = "kernel_outputs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("kernel_cases.id"), nullable=False, index=True
    )
    artifact_type: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_id: Mapped[str] = mapped_column(String(36), nullable=False)
    content: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


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


class SQLAlchemyKernelRepository:
    """SQL-backed Kernel repository with append-only audit collections."""

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
            Base.metadata.create_all(self.engine)

    @property
    def persistence_name(self) -> str:
        return f"sqlalchemy-{self.engine.dialect.name}"

    def create_schema(self) -> None:
        Base.metadata.create_all(self.engine)

    def close(self) -> None:
        self.engine.dispose()

    def save_case(self, case: Case) -> Case:
        with self._sessions.begin() as session:
            row = session.get(CaseRow, str(case.id))
            if row is None:
                row = CaseRow(
                    id=str(case.id),
                    title=case.title,
                    description=case.description,
                    owner_id=str(case.owner_id),
                    organization_id=str(case.organization_id),
                    sensitivity=case.sensitivity.value,
                    status=case.status.value,
                    version=case.version,
                    created_at=case.created_at,
                    updated_at=case.updated_at,
                )
                session.add(row)
            else:
                row.title = case.title
                row.description = case.description
                row.owner_id = str(case.owner_id)
                row.organization_id = str(case.organization_id)
                row.sensitivity = case.sensitivity.value
                row.status = case.status.value
                row.version = case.version
                row.updated_at = case.updated_at

            for event in case.events:
                if session.get(CaseEventRow, str(event.id)) is None:
                    session.add(
                        CaseEventRow(
                            id=str(event.id),
                            case_id=str(case.id),
                            event_type=event.event_type,
                            actor_id=str(event.actor_id),
                            details=event.details,
                            created_at=event.created_at,
                        )
                    )
        return self.get_case(case.id)

    def get_case(self, case_id: UUID) -> Case:
        with self._sessions() as session:
            row = session.get(CaseRow, str(case_id))
            if row is None:
                raise CaseNotFoundError(str(case_id))
            event_rows = session.scalars(
                select(CaseEventRow)
                .where(CaseEventRow.case_id == str(case_id))
                .order_by(CaseEventRow.created_at, CaseEventRow.id)
            ).all()
            return self._case_from_rows(row, event_rows)

    def list_cases(self) -> list[Case]:
        with self._sessions() as session:
            rows = session.scalars(
                select(CaseRow).order_by(CaseRow.created_at, CaseRow.id)
            ).all()
            return [self.get_case(UUID(row.id)) for row in rows]

    def append_approval(self, approval: ApprovalRecord) -> ApprovalRecord:
        with self._sessions.begin() as session:
            existing = session.get(ApprovalRow, str(approval.id))
            if existing is None:
                session.add(
                    ApprovalRow(
                        id=str(approval.id),
                        case_id=str(approval.case_id),
                        approver_id=str(approval.approver_id),
                        decision=approval.decision.value,
                        rationale=approval.rationale,
                        conditions=list(approval.conditions),
                        created_at=approval.created_at,
                    )
                )
        return approval

    def approvals_for_case(self, case_id: UUID) -> tuple[ApprovalRecord, ...]:
        with self._sessions() as session:
            rows = session.scalars(
                select(ApprovalRow)
                .where(ApprovalRow.case_id == str(case_id))
                .order_by(ApprovalRow.created_at, ApprovalRow.id)
            ).all()
            return tuple(
                ApprovalRecord(
                    id=UUID(row.id),
                    case_id=UUID(row.case_id),
                    approver_id=UUID(row.approver_id),
                    decision=ApprovalDecision(row.decision),
                    rationale=row.rationale,
                    conditions=tuple(row.conditions or ()),
                    created_at=_aware(row.created_at),
                )
                for row in rows
            )

    def append_evidence(self, evidence: EvidenceReference) -> EvidenceReference:
        with self._sessions.begin() as session:
            existing = session.get(EvidenceRow, str(evidence.id))
            if existing is None:
                session.add(
                    EvidenceRow(
                        id=str(evidence.id),
                        case_id=str(evidence.case_id),
                        label=evidence.label,
                        uri=evidence.uri,
                        sensitivity=evidence.sensitivity.value,
                        created_at=evidence.created_at,
                    )
                )
        return evidence

    def evidence_for_case(self, case_id: UUID) -> tuple[EvidenceReference, ...]:
        with self._sessions() as session:
            rows = session.scalars(
                select(EvidenceRow)
                .where(EvidenceRow.case_id == str(case_id))
                .order_by(EvidenceRow.created_at, EvidenceRow.id)
            ).all()
            return tuple(
                EvidenceReference(
                    id=UUID(row.id),
                    case_id=UUID(row.case_id),
                    label=row.label,
                    uri=row.uri,
                    sensitivity=Sensitivity(row.sensitivity),
                    created_at=_aware(row.created_at),
                )
                for row in rows
            )

    def append_output(self, output: OutputArtifact) -> OutputArtifact:
        with self._sessions.begin() as session:
            existing = session.get(OutputRow, str(output.id))
            if existing is None:
                session.add(
                    OutputRow(
                        id=str(output.id),
                        case_id=str(output.case_id),
                        artifact_type=output.artifact_type,
                        owner_id=str(output.owner_id),
                        content=output.content,
                        version=output.version,
                        status=output.status.value,
                        created_at=output.created_at,
                    )
                )
        return output

    def outputs_for_case(self, case_id: UUID) -> tuple[OutputArtifact, ...]:
        with self._sessions() as session:
            rows = session.scalars(
                select(OutputRow)
                .where(OutputRow.case_id == str(case_id))
                .order_by(OutputRow.created_at, OutputRow.id)
            ).all()
            return tuple(
                OutputArtifact(
                    id=UUID(row.id),
                    case_id=UUID(row.case_id),
                    artifact_type=row.artifact_type,
                    owner_id=UUID(row.owner_id),
                    content=row.content,
                    version=row.version,
                    status=ArtifactStatus(row.status),
                    created_at=_aware(row.created_at),
                )
                for row in rows
            )

    @staticmethod
    def _case_from_rows(row: CaseRow, event_rows: list[CaseEventRow]) -> Case:
        return Case(
            id=UUID(row.id),
            title=row.title,
            description=row.description,
            owner_id=UUID(row.owner_id),
            organization_id=UUID(row.organization_id),
            sensitivity=Sensitivity(row.sensitivity),
            status=CaseStatus(row.status),
            version=row.version,
            created_at=_aware(row.created_at),
            updated_at=_aware(row.updated_at),
            events=[
                CaseEvent(
                    id=UUID(event.id),
                    event_type=event.event_type,
                    actor_id=UUID(event.actor_id),
                    details=event.details,
                    created_at=_aware(event.created_at),
                )
                for event in event_rows
            ],
        )

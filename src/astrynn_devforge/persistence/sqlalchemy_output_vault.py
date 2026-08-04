from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
    select,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
)

from astrynn_devforge.dataforge import (
    ArtifactNotFoundError,
    DuplicateArtifactVersionError,
    VaultArtifactVersion,
    VaultDecision,
    VaultProofReceipt,
)
from astrynn_devforge.kernel import ArtifactStatus, Sensitivity


class OutputVaultBase(DeclarativeBase):
    pass


class VaultArtifactVersionRow(OutputVaultBase):
    __tablename__ = "output_vault_artifact_versions"
    __table_args__ = (
        UniqueConstraint(
            "artifact_id",
            "version",
            name="uq_output_vault_artifact_version",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    artifact_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class VaultProofReceiptRow(OutputVaultBase):
    __tablename__ = "output_vault_proof_receipts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    artifact_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )
    artifact_version_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("output_vault_artifact_versions.id"),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


def _optional_uuid(value: str | None) -> UUID | None:
    return UUID(value) if value else None


class SQLAlchemyOutputVaultRepository:
    """Append-only Output Vault persistence using SQLAlchemy."""

    def __init__(
        self,
        database_url: str,
        *,
        create_schema: bool = False,
    ) -> None:
        resolved_url = database_url.strip()
        if not resolved_url:
            raise ValueError("Database URL is required")

        self._engine = create_engine(resolved_url)
        self._sessions = sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
        )

        if create_schema:
            self.create_schema()

    @property
    def persistence_name(self) -> str:
        return f"sqlalchemy-{self._engine.dialect.name}"

    def create_schema(self) -> None:
        OutputVaultBase.metadata.create_all(self._engine)

    def close(self) -> None:
        self._engine.dispose()

    def append_version(
        self,
        version: VaultArtifactVersion,
    ) -> VaultArtifactVersion:
        with self._sessions.begin() as session:
            duplicate_version = session.scalar(
                select(VaultArtifactVersionRow).where(
                    VaultArtifactVersionRow.artifact_id
                    == str(version.artifact_id),
                    VaultArtifactVersionRow.version
                    == version.version,
                )
            )
            if duplicate_version is not None:
                raise DuplicateArtifactVersionError(
                    f"Artifact {version.artifact_id} already has "
                    f"version {version.version}"
                )

            if session.get(
                VaultArtifactVersionRow,
                str(version.id),
            ) is not None:
                raise DuplicateArtifactVersionError(
                    f"Version id {version.id} already exists"
                )

            session.add(
                VaultArtifactVersionRow(
                    id=str(version.id),
                    artifact_id=str(version.artifact_id),
                    version=version.version,
                    payload=version.to_dict(),
                    created_at=version.created_at,
                )
            )

        return version

    def append_receipt(
        self,
        receipt: VaultProofReceipt,
    ) -> VaultProofReceipt:
        with self._sessions.begin() as session:
            if session.get(
                VaultProofReceiptRow,
                str(receipt.id),
            ) is not None:
                raise ValueError(
                    f"Receipt id {receipt.id} already exists"
                )

            version_row = session.get(
                VaultArtifactVersionRow,
                str(receipt.artifact_version_id),
            )
            if version_row is None:
                raise ArtifactNotFoundError(
                    str(receipt.artifact_version_id)
                )

            session.add(
                VaultProofReceiptRow(
                    id=str(receipt.id),
                    artifact_id=str(receipt.artifact_id),
                    artifact_version_id=str(
                        receipt.artifact_version_id
                    ),
                    version=receipt.version,
                    payload=receipt.to_dict(),
                    created_at=receipt.created_at,
                )
            )

        return receipt

    def get_version(
        self,
        version_id: UUID,
    ) -> VaultArtifactVersion:
        with self._sessions() as session:
            row = session.get(
                VaultArtifactVersionRow,
                str(version_id),
            )

        if row is None:
            raise ArtifactNotFoundError(str(version_id))

        return self._artifact_from_payload(row.payload)

    def versions_for_artifact(
        self,
        artifact_id: UUID,
    ) -> tuple[VaultArtifactVersion, ...]:
        with self._sessions() as session:
            rows = session.scalars(
                select(VaultArtifactVersionRow)
                .where(
                    VaultArtifactVersionRow.artifact_id
                    == str(artifact_id)
                )
                .order_by(VaultArtifactVersionRow.version)
            ).all()

        return tuple(
            self._artifact_from_payload(row.payload)
            for row in rows
        )

    def latest_version(
        self,
        artifact_id: UUID,
    ) -> VaultArtifactVersion:
        with self._sessions() as session:
            row = session.scalar(
                select(VaultArtifactVersionRow)
                .where(
                    VaultArtifactVersionRow.artifact_id
                    == str(artifact_id)
                )
                .order_by(VaultArtifactVersionRow.version.desc())
                .limit(1)
            )

        if row is None:
            raise ArtifactNotFoundError(str(artifact_id))

        return self._artifact_from_payload(row.payload)

    def receipts_for_artifact(
        self,
        artifact_id: UUID,
    ) -> tuple[VaultProofReceipt, ...]:
        with self._sessions() as session:
            rows = session.scalars(
                select(VaultProofReceiptRow)
                .where(
                    VaultProofReceiptRow.artifact_id
                    == str(artifact_id)
                )
                .order_by(VaultProofReceiptRow.version)
            ).all()

        return tuple(
            self._receipt_from_payload(row.payload)
            for row in rows
        )

    def list_latest(
        self,
    ) -> tuple[VaultArtifactVersion, ...]:
        with self._sessions() as session:
            rows = session.scalars(
                select(VaultArtifactVersionRow).order_by(
                    VaultArtifactVersionRow.created_at
                )
            ).all()

        latest_by_artifact: dict[
            UUID,
            VaultArtifactVersion,
        ] = {}

        for row in rows:
            artifact = self._artifact_from_payload(row.payload)
            current = latest_by_artifact.get(
                artifact.artifact_id
            )
            if current is None or artifact.version > current.version:
                latest_by_artifact[artifact.artifact_id] = artifact

        return tuple(
            sorted(
                latest_by_artifact.values(),
                key=lambda item: item.created_at,
            )
        )

    @staticmethod
    def _artifact_from_payload(
        payload: dict[str, Any],
    ) -> VaultArtifactVersion:
        decision = payload.get("decision")

        return VaultArtifactVersion(
            artifact_id=UUID(payload["artifact_id"]),
            case_id=UUID(payload["case_id"]),
            owner_id=UUID(payload["owner_id"]),
            created_by=UUID(payload["created_by"]),
            artifact_type=payload["artifact_type"],
            title=payload["title"],
            content=payload["content"],
            sensitivity=Sensitivity(payload["sensitivity"]),
            version=int(payload["version"]),
            status=ArtifactStatus(payload["status"]),
            decision=(
                VaultDecision(decision)
                if decision is not None
                else None
            ),
            conditions=tuple(payload.get("conditions", ())),
            test_references=tuple(
                payload.get("test_references", ())
            ),
            evidence_references=tuple(
                payload.get("evidence_references", ())
            ),
            parent_version_id=_optional_uuid(
                payload.get("parent_version_id")
            ),
            change_summary=payload.get(
                "change_summary",
                "",
            ),
            id=UUID(payload["id"]),
            created_at=datetime.fromisoformat(
                payload["created_at"]
            ),
        )

    @staticmethod
    def _receipt_from_payload(
        payload: dict[str, Any],
    ) -> VaultProofReceipt:
        return VaultProofReceipt(
            artifact_id=UUID(payload["artifact_id"]),
            artifact_version_id=UUID(
                payload["artifact_version_id"]
            ),
            case_id=UUID(payload["case_id"]),
            version=int(payload["version"]),
            evaluator_id=UUID(payload["evaluator_id"]),
            decision=VaultDecision(payload["decision"]),
            conditions=tuple(payload.get("conditions", ())),
            test_references=tuple(
                payload.get("test_references", ())
            ),
            evidence_references=tuple(
                payload.get("evidence_references", ())
            ),
            artifact_integrity_hash=payload[
                "artifact_integrity_hash"
            ],
            methodology_version=payload[
                "methodology_version"
            ],
            id=UUID(payload["id"]),
            created_at=datetime.fromisoformat(
                payload["created_at"]
            ),
        )

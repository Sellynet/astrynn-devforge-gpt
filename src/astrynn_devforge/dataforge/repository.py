from __future__ import annotations

from copy import deepcopy
from uuid import UUID

from .models import VaultArtifactVersion, VaultProofReceipt


class ArtifactNotFoundError(KeyError):
    pass


class DuplicateArtifactVersionError(ValueError):
    pass


class InMemoryOutputVaultRepository:
    """Append-only development repository for artifact versions and proof receipts."""

    def __init__(self) -> None:
        self._versions: list[VaultArtifactVersion] = []
        self._receipts: list[VaultProofReceipt] = []

    def append_version(self, version: VaultArtifactVersion) -> VaultArtifactVersion:
        existing = self.versions_for_artifact(version.artifact_id)
        if any(item.version == version.version for item in existing):
            raise DuplicateArtifactVersionError(
                f"Artifact {version.artifact_id} already has version {version.version}"
            )
        if any(item.id == version.id for item in self._versions):
            raise DuplicateArtifactVersionError(f"Version id {version.id} already exists")
        self._versions.append(deepcopy(version))
        return deepcopy(version)

    def append_receipt(self, receipt: VaultProofReceipt) -> VaultProofReceipt:
        if any(item.id == receipt.id for item in self._receipts):
            raise ValueError(f"Receipt id {receipt.id} already exists")
        self._receipts.append(deepcopy(receipt))
        return deepcopy(receipt)

    def get_version(self, version_id: UUID) -> VaultArtifactVersion:
        for item in self._versions:
            if item.id == version_id:
                return deepcopy(item)
        raise ArtifactNotFoundError(str(version_id))

    def versions_for_artifact(self, artifact_id: UUID) -> tuple[VaultArtifactVersion, ...]:
        matches = [item for item in self._versions if item.artifact_id == artifact_id]
        return tuple(deepcopy(item) for item in sorted(matches, key=lambda item: item.version))

    def latest_version(self, artifact_id: UUID) -> VaultArtifactVersion:
        versions = self.versions_for_artifact(artifact_id)
        if not versions:
            raise ArtifactNotFoundError(str(artifact_id))
        return versions[-1]

    def receipts_for_artifact(self, artifact_id: UUID) -> tuple[VaultProofReceipt, ...]:
        matches = [item for item in self._receipts if item.artifact_id == artifact_id]
        return tuple(deepcopy(item) for item in sorted(matches, key=lambda item: item.version))

    def list_latest(self) -> tuple[VaultArtifactVersion, ...]:
        artifact_ids = {item.artifact_id for item in self._versions}
        latest = [self.latest_version(artifact_id) for artifact_id in artifact_ids]
        return tuple(sorted(latest, key=lambda item: item.created_at))

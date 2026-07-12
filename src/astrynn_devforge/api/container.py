from __future__ import annotations

import os
from dataclasses import dataclass

from astrynn_devforge.kernel import (
    InMemoryKernelRepository,
    KernelRepository,
    KernelService,
)
from astrynn_devforge.persistence import SQLAlchemyKernelRepository

from .auth import InMemoryTokenAuthenticator, Principal


@dataclass(slots=True)
class ApplicationContainer:
    kernel_repository: KernelRepository
    kernel_service: KernelService
    authenticator: InMemoryTokenAuthenticator


def _environment_flag(name: str, *, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"{name} must be true or false")


def _build_repository(
    *,
    repository: KernelRepository | None,
    database_url: str | None,
    create_schema: bool | None,
) -> KernelRepository:
    if repository is not None:
        return repository

    resolved_url = database_url or os.getenv("ASTRYNN_DATABASE_URL", "").strip()
    if not resolved_url:
        return InMemoryKernelRepository()

    auto_create = (
        create_schema
        if create_schema is not None
        else _environment_flag(
            "ASTRYNN_AUTO_CREATE_SCHEMA",
            default=resolved_url.startswith("sqlite"),
        )
    )
    return SQLAlchemyKernelRepository(resolved_url, create_schema=auto_create)


def build_container(
    token_principals: dict[str, Principal] | None = None,
    *,
    repository: KernelRepository | None = None,
    database_url: str | None = None,
    create_schema: bool | None = None,
) -> ApplicationContainer:
    kernel_repository = _build_repository(
        repository=repository,
        database_url=database_url,
        create_schema=create_schema,
    )
    authenticator = (
        InMemoryTokenAuthenticator(token_principals)
        if token_principals is not None
        else InMemoryTokenAuthenticator.from_environment()
    )
    return ApplicationContainer(
        kernel_repository=kernel_repository,
        kernel_service=KernelService(kernel_repository),
        authenticator=authenticator,
    )

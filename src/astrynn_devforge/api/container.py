from __future__ import annotations

from dataclasses import dataclass

from astrynn_devforge.kernel import InMemoryKernelRepository, KernelService

from .auth import InMemoryTokenAuthenticator, Principal


@dataclass(slots=True)
class ApplicationContainer:
    kernel_repository: InMemoryKernelRepository
    kernel_service: KernelService
    authenticator: InMemoryTokenAuthenticator


def build_container(
    token_principals: dict[str, Principal] | None = None,
) -> ApplicationContainer:
    repository = InMemoryKernelRepository()
    authenticator = (
        InMemoryTokenAuthenticator(token_principals)
        if token_principals is not None
        else InMemoryTokenAuthenticator.from_environment()
    )
    return ApplicationContainer(
        kernel_repository=repository,
        kernel_service=KernelService(repository),
        authenticator=authenticator,
    )

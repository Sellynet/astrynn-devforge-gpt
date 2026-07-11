from __future__ import annotations

from dataclasses import dataclass

from astrynn_devforge.kernel import InMemoryKernelRepository, KernelService


@dataclass(slots=True)
class ApplicationContainer:
    kernel_repository: InMemoryKernelRepository
    kernel_service: KernelService


def build_container() -> ApplicationContainer:
    repository = InMemoryKernelRepository()
    return ApplicationContainer(
        kernel_repository=repository,
        kernel_service=KernelService(repository),
    )

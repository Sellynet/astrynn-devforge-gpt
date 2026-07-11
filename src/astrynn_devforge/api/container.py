from __future__ import annotations

from dataclasses import dataclass, field

from astrynn_devforge.kernel import InMemoryKernelRepository, KernelService


@dataclass(slots=True)
class RuntimeContainer:
    kernel_repository: InMemoryKernelRepository = field(
        default_factory=InMemoryKernelRepository
    )
    kernel_service: KernelService = field(init=False)

    def __post_init__(self) -> None:
        self.kernel_service = KernelService(self.kernel_repository)

    def counts(self) -> dict[str, int]:
        return {
            "cases": len(self.kernel_repository.list_cases()),
        }

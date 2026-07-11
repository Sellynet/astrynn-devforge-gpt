from __future__ import annotations

from dataclasses import dataclass
import os


def _parse_origins(raw: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in raw.split(",") if item.strip())


@dataclass(frozen=True, slots=True)
class APISettings:
    environment: str = "development"
    version: str = "0.1.0"
    persistence_mode: str = "in-memory"
    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: tuple[str, ...] = ()

    @classmethod
    def from_environment(cls) -> "APISettings":
        return cls(
            environment=os.getenv("ASTRYNN_ENVIRONMENT", "development").strip()
            or "development",
            version=os.getenv("ASTRYNN_API_VERSION", "0.1.0").strip() or "0.1.0",
            persistence_mode=os.getenv(
                "ASTRYNN_PERSISTENCE_MODE", "in-memory"
            ).strip()
            or "in-memory",
            host=os.getenv("ASTRYNN_API_HOST", "127.0.0.1").strip()
            or "127.0.0.1",
            port=int(os.getenv("ASTRYNN_API_PORT", "8000")),
            cors_origins=_parse_origins(os.getenv("ASTRYNN_CORS_ORIGINS", "")),
        )

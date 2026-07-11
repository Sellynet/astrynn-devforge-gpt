from __future__ import annotations

from enum import StrEnum


class VaultDecision(StrEnum):
    APPROVED = "APPROVED"
    APPROVED_WITH_CONDITIONS = "APPROVED_WITH_CONDITIONS"
    REJECTED = "REJECTED"
    REQUIRES_SPECIALIST_REVIEW = "REQUIRES_SPECIALIST_REVIEW"


class ExportFormat(StrEnum):
    JSON = "JSON"
    MARKDOWN = "MARKDOWN"

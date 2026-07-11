from __future__ import annotations

from enum import StrEnum


class ARIATestOutcome(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"


class ARIAFindingSeverity(StrEnum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ARIAFindingDisposition(StrEnum):
    REMEDIATED = "REMEDIATED"
    ACCEPTED_RISK = "ACCEPTED_RISK"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class ARIAVerdict(StrEnum):
    PASS = "PASS"
    PASS_WITH_REMEDIATION = "PASS_WITH_REMEDIATION"
    BLOCKED = "BLOCKED"

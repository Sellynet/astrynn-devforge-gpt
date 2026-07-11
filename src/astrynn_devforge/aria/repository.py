from __future__ import annotations

from copy import deepcopy
from uuid import UUID

from astrynn_devforge.oaaa.enums import ARIATestFamily

from .models import (
    ARIACampaign,
    ARIAFinding,
    ARIAFindingResolution,
    ARIAReceipt,
    ARIATestRecord,
)


class ARIACampaignNotFoundError(KeyError):
    pass


class ARIAFindingNotFoundError(KeyError):
    pass


class InMemoryARIARepository:
    """Append-only development repository for ARIA campaigns and evidence."""

    def __init__(self) -> None:
        self._campaigns: dict[UUID, ARIACampaign] = {}
        self._tests: list[ARIATestRecord] = []
        self._findings: list[ARIAFinding] = []
        self._resolutions: list[ARIAFindingResolution] = []
        self._receipts: list[ARIAReceipt] = []

    def append_campaign(self, campaign: ARIACampaign) -> ARIACampaign:
        if campaign.id in self._campaigns:
            raise ValueError(f"ARIA campaign {campaign.id} already exists")
        self._campaigns[campaign.id] = deepcopy(campaign)
        return deepcopy(campaign)

    def get_campaign(self, campaign_id: UUID) -> ARIACampaign:
        try:
            return deepcopy(self._campaigns[campaign_id])
        except KeyError as exc:
            raise ARIACampaignNotFoundError(str(campaign_id)) from exc

    def append_test(self, record: ARIATestRecord) -> ARIATestRecord:
        if any(item.id == record.id for item in self._tests):
            raise ValueError(f"ARIA test record {record.id} already exists")
        self._tests.append(deepcopy(record))
        return deepcopy(record)

    def tests_for_campaign(self, campaign_id: UUID) -> tuple[ARIATestRecord, ...]:
        return tuple(
            deepcopy(item) for item in self._tests if item.campaign_id == campaign_id
        )

    def tests_for_family(
        self, campaign_id: UUID, family: ARIATestFamily
    ) -> tuple[ARIATestRecord, ...]:
        return tuple(
            deepcopy(item)
            for item in self._tests
            if item.campaign_id == campaign_id and item.family == family
        )

    def latest_tests_by_family(
        self, campaign_id: UUID
    ) -> dict[ARIATestFamily, ARIATestRecord]:
        latest: dict[ARIATestFamily, ARIATestRecord] = {}
        for record in self.tests_for_campaign(campaign_id):
            previous = latest.get(record.family)
            if previous is None or record.run_number > previous.run_number:
                latest[record.family] = record
        return latest

    def append_finding(self, finding: ARIAFinding) -> ARIAFinding:
        if any(item.id == finding.id for item in self._findings):
            raise ValueError(f"ARIA finding {finding.id} already exists")
        self._findings.append(deepcopy(finding))
        return deepcopy(finding)

    def get_finding(self, finding_id: UUID) -> ARIAFinding:
        for finding in self._findings:
            if finding.id == finding_id:
                return deepcopy(finding)
        raise ARIAFindingNotFoundError(str(finding_id))

    def findings_for_campaign(self, campaign_id: UUID) -> tuple[ARIAFinding, ...]:
        return tuple(
            deepcopy(item) for item in self._findings if item.campaign_id == campaign_id
        )

    def append_resolution(
        self, resolution: ARIAFindingResolution
    ) -> ARIAFindingResolution:
        if any(item.id == resolution.id for item in self._resolutions):
            raise ValueError(f"ARIA resolution {resolution.id} already exists")
        self._resolutions.append(deepcopy(resolution))
        return deepcopy(resolution)

    def resolutions_for_finding(
        self, finding_id: UUID
    ) -> tuple[ARIAFindingResolution, ...]:
        return tuple(
            deepcopy(item)
            for item in self._resolutions
            if item.finding_id == finding_id
        )

    def latest_resolution(
        self, finding_id: UUID
    ) -> ARIAFindingResolution | None:
        records = self.resolutions_for_finding(finding_id)
        return records[-1] if records else None

    def append_receipt(self, receipt: ARIAReceipt) -> ARIAReceipt:
        if any(item.id == receipt.id for item in self._receipts):
            raise ValueError(f"ARIA receipt {receipt.id} already exists")
        expected_version = len(self.receipts_for_campaign(receipt.campaign_id)) + 1
        if receipt.version != expected_version:
            raise ValueError(
                f"Expected ARIA receipt version {expected_version}, got {receipt.version}"
            )
        self._receipts.append(deepcopy(receipt))
        return deepcopy(receipt)

    def receipts_for_campaign(self, campaign_id: UUID) -> tuple[ARIAReceipt, ...]:
        return tuple(
            deepcopy(item) for item in self._receipts if item.campaign_id == campaign_id
        )

    def latest_receipt(self, campaign_id: UUID) -> ARIAReceipt | None:
        receipts = self.receipts_for_campaign(campaign_id)
        return receipts[-1] if receipts else None

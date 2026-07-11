from __future__ import annotations

from uuid import UUID

from astrynn_devforge.kernel import (
    ArtifactStatus,
    EvidenceReference,
    InMemoryKernelRepository,
    OutputArtifact,
    Sensitivity,
)
from astrynn_devforge.oaaa.enums import ARIATestFamily, BlueprintStatus
from astrynn_devforge.oaaa.repository import InMemoryAgentBlueprintRepository

from .enums import (
    ARIAFindingDisposition,
    ARIAFindingSeverity,
    ARIATestOutcome,
    ARIAVerdict,
)
from .models import (
    ARIACampaign,
    ARIAFinding,
    ARIAFindingInput,
    ARIAFindingResolution,
    ARIAReceipt,
    ARIATestRecord,
)
from .repository import InMemoryARIARepository


class ARIAValidationError(ValueError):
    pass


class ARIAFinalizationError(PermissionError):
    pass


class ARIAStaleBlueprintError(ValueError):
    pass


class ARIATestRegisterService:
    """Append-only adversarial test register bound to an OAAA safety fingerprint."""

    def __init__(
        self,
        kernel_repository: InMemoryKernelRepository,
        blueprint_repository: InMemoryAgentBlueprintRepository,
        aria_repository: InMemoryARIARepository,
    ) -> None:
        self.kernel_repository = kernel_repository
        self.blueprint_repository = blueprint_repository
        self.aria_repository = aria_repository

    def create_campaign(
        self,
        *,
        blueprint_id: UUID,
        created_by: UUID,
    ) -> ARIACampaign:
        blueprint = self.blueprint_repository.latest_version(blueprint_id)
        if blueprint.status not in {
            BlueprintStatus.CLEARED,
            BlueprintStatus.APPROVED,
            BlueprintStatus.SUSPENDED,
        }:
            raise ARIAValidationError(
                "ARIA requires a CLEARED, APPROVED or SUSPENDED blueprint"
            )
        required_families = tuple(
            dict.fromkeys(requirement.family for requirement in blueprint.aria_test_plan)
        )
        campaign = ARIACampaign(
            case_id=blueprint.case_id,
            blueprint_id=blueprint.blueprint_id,
            blueprint_version_id=blueprint.id,
            blueprint_fingerprint=blueprint.safety_fingerprint,
            owner_id=blueprint.owner_id,
            created_by=created_by,
            required_families=required_families,
            sensitivity=blueprint.sensitivity,
        )
        stored = self.aria_repository.append_campaign(campaign)
        self.kernel_repository.append_evidence(
            EvidenceReference(
                case_id=stored.case_id,
                label="ARIA adversarial test campaign created",
                uri=f"aria://campaigns/{stored.id}",
                sensitivity=stored.sensitivity,
            )
        )
        return stored

    def record_test(
        self,
        *,
        campaign_id: UUID,
        family: ARIATestFamily,
        objective: str,
        adversarial_input: str,
        expected_behavior: str,
        actual_behavior: str,
        outcome: ARIATestOutcome,
        executed_by: UUID,
        evidence_references: tuple[str, ...],
        findings: tuple[ARIAFindingInput, ...] = (),
    ) -> tuple[ARIATestRecord, tuple[ARIAFinding, ...]]:
        campaign = self.aria_repository.get_campaign(campaign_id)
        self._assert_campaign_fingerprint_current(campaign)
        if family not in campaign.required_families:
            raise ARIAValidationError(
                f"Test family {family.value} is not declared in the blueprint ARIA plan"
            )
        if outcome in {ARIATestOutcome.FAIL, ARIATestOutcome.ERROR} and not findings:
            raise ARIAValidationError("A failed or errored ARIA test requires a finding")

        previous = self.aria_repository.tests_for_family(campaign_id, family)
        record = ARIATestRecord(
            campaign_id=campaign.id,
            case_id=campaign.case_id,
            blueprint_id=campaign.blueprint_id,
            blueprint_version_id=campaign.blueprint_version_id,
            blueprint_fingerprint=campaign.blueprint_fingerprint,
            family=family,
            objective=objective,
            adversarial_input=adversarial_input,
            expected_behavior=expected_behavior,
            actual_behavior=actual_behavior,
            outcome=outcome,
            executed_by=executed_by,
            evidence_references=evidence_references,
            run_number=len(previous) + 1,
        )
        stored_record = self.aria_repository.append_test(record)
        stored_findings = tuple(
            self.aria_repository.append_finding(
                ARIAFinding(
                    campaign_id=campaign.id,
                    test_record_id=stored_record.id,
                    severity=item.severity,
                    title=item.title,
                    description=item.description,
                    remediation=item.remediation,
                )
            )
            for item in findings
        )
        self.kernel_repository.append_evidence(
            EvidenceReference(
                case_id=campaign.case_id,
                label=f"ARIA {family.value} run {stored_record.run_number}",
                uri=f"aria://tests/{stored_record.id}",
                sensitivity=campaign.sensitivity,
            )
        )
        return stored_record, stored_findings

    def resolve_finding(
        self,
        *,
        finding_id: UUID,
        disposition: ARIAFindingDisposition,
        resolved_by: UUID,
        rationale: str,
        evidence_references: tuple[str, ...],
    ) -> ARIAFindingResolution:
        finding = self.aria_repository.get_finding(finding_id)
        if self.aria_repository.latest_resolution(finding_id) is not None:
            raise ARIAValidationError("ARIA finding already has a recorded disposition")
        if (
            finding.severity == ARIAFindingSeverity.CRITICAL
            and disposition == ARIAFindingDisposition.ACCEPTED_RISK
        ):
            raise ARIAFinalizationError(
                "Critical ARIA findings cannot be closed as accepted risk"
            )
        resolution = ARIAFindingResolution(
            finding_id=finding.id,
            disposition=disposition,
            resolved_by=resolved_by,
            rationale=rationale,
            evidence_references=evidence_references,
        )
        stored = self.aria_repository.append_resolution(resolution)
        campaign = self.aria_repository.get_campaign(finding.campaign_id)
        self.kernel_repository.append_evidence(
            EvidenceReference(
                case_id=campaign.case_id,
                label=f"ARIA finding disposition: {disposition.value}",
                uri=f"aria://findings/{finding.id}/resolutions/{stored.id}",
                sensitivity=campaign.sensitivity,
            )
        )
        return stored

    def finalize_campaign(
        self,
        *,
        campaign_id: UUID,
        finalized_by: UUID,
    ) -> ARIAReceipt:
        campaign = self.aria_repository.get_campaign(campaign_id)
        self._assert_campaign_fingerprint_current(campaign)
        if (
            campaign.sensitivity in {Sensitivity.ORANGE, Sensitivity.RED}
            and finalized_by == campaign.owner_id
        ):
            raise ARIAFinalizationError(
                "ORANGE and RED ARIA campaigns require owner/finalizer separation"
            )

        latest_tests = self.aria_repository.latest_tests_by_family(campaign.id)
        missing = set(campaign.required_families) - set(latest_tests)
        if missing:
            names = ", ".join(sorted(item.value for item in missing))
            raise ARIAFinalizationError(f"ARIA campaign is missing required tests: {names}")

        findings = self.aria_repository.findings_for_campaign(campaign.id)
        open_findings = tuple(
            finding
            for finding in findings
            if self.aria_repository.latest_resolution(finding.id) is None
        )
        unresolved_critical = sum(
            finding.severity == ARIAFindingSeverity.CRITICAL
            for finding in open_findings
        )
        unresolved_high = sum(
            finding.severity == ARIAFindingSeverity.HIGH for finding in open_findings
        )
        latest_outcomes = {record.outcome for record in latest_tests.values()}

        if unresolved_critical or latest_outcomes & {
            ARIATestOutcome.FAIL,
            ARIATestOutcome.ERROR,
        }:
            verdict = ARIAVerdict.BLOCKED
        elif open_findings:
            verdict = ARIAVerdict.PASS_WITH_REMEDIATION
        else:
            verdict = ARIAVerdict.PASS

        evidence_references = tuple(
            dict.fromkeys(
                reference
                for record in latest_tests.values()
                for reference in record.evidence_references
            )
        )
        receipt = ARIAReceipt(
            campaign_id=campaign.id,
            case_id=campaign.case_id,
            blueprint_id=campaign.blueprint_id,
            blueprint_version_id=campaign.blueprint_version_id,
            blueprint_fingerprint=campaign.blueprint_fingerprint,
            verdict=verdict,
            latest_test_record_ids=tuple(
                latest_tests[family].id for family in campaign.required_families
            ),
            finding_ids=tuple(item.id for item in findings),
            open_finding_ids=tuple(item.id for item in open_findings),
            unresolved_critical_findings=unresolved_critical,
            unresolved_high_findings=unresolved_high,
            evidence_references=evidence_references,
            finalized_by=finalized_by,
            version=len(self.aria_repository.receipts_for_campaign(campaign.id)) + 1,
        )
        stored = self.aria_repository.append_receipt(receipt)
        artifact_status = (
            ArtifactStatus.REJECTED
            if stored.verdict == ARIAVerdict.BLOCKED
            else ArtifactStatus.APPROVED
        )
        self.kernel_repository.append_output(
            OutputArtifact(
                case_id=campaign.case_id,
                artifact_type="ARIA_RECEIPT",
                owner_id=campaign.owner_id,
                content=stored.to_dict(),
                version=stored.version,
                status=artifact_status,
            )
        )
        self.kernel_repository.append_evidence(
            EvidenceReference(
                case_id=campaign.case_id,
                label=f"ARIA Receipt v{stored.version}: {stored.verdict.value}",
                uri=f"aria://receipts/{stored.id}",
                sensitivity=campaign.sensitivity,
            )
        )
        return stored

    def _assert_campaign_fingerprint_current(self, campaign: ARIACampaign) -> None:
        latest = self.blueprint_repository.latest_version(campaign.blueprint_id)
        if latest.case_id != campaign.case_id:
            raise ARIAStaleBlueprintError("ARIA campaign case no longer matches blueprint")
        if latest.safety_fingerprint != campaign.blueprint_fingerprint:
            raise ARIAStaleBlueprintError(
                "Blueprint changed materially after the ARIA campaign was created"
            )

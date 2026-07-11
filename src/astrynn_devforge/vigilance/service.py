from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from uuid import UUID, uuid4

from astrynn_devforge.kernel import (
    ArtifactStatus,
    EvidenceReference,
    InMemoryKernelRepository,
    OutputArtifact,
    Sensitivity,
)

from .enums import (
    ApprovalDecision,
    AuthorizationOutcome,
    GrantStatus,
    PermissionAction,
    PermissionEventType,
)
from .models import (
    ActionAuthorizationReceipt,
    PermissionApprovalRecord,
    PermissionApprovalRequest,
    PermissionEvent,
    PermissionGrantReceipt,
    PermissionGrantVersion,
    utc_now,
)
from .repository import InMemoryVigilanceRepository


class PermissionTransitionError(ValueError):
    pass


class PermissionBoundaryError(PermissionError):
    pass


class PermissionApprovalError(PermissionError):
    pass


class StalePermissionError(ValueError):
    pass


class VigilancePermissionService:
    """Least-privilege permission control. It authorizes; it never executes tools."""

    def __init__(
        self,
        kernel_repository: InMemoryKernelRepository,
        vigilance_repository: InMemoryVigilanceRepository,
    ) -> None:
        self.kernel_repository = kernel_repository
        self.vigilance_repository = vigilance_repository

    def create_draft(
        self,
        *,
        case_id: UUID,
        blueprint_id: UUID,
        blueprint_version_id: UUID,
        blueprint_fingerprint: str,
        subject_id: UUID,
        owner_id: UUID,
        created_by: UUID,
        tool_name: str,
        resource_prefixes: tuple[str, ...],
        allowed_actions: tuple[PermissionAction, ...],
        denied_actions: tuple[PermissionAction, ...],
        approval_required_actions: tuple[PermissionAction, ...],
        sensitivity: Sensitivity,
        reason: str,
        review_at: datetime,
        expires_at: datetime,
    ) -> PermissionGrantVersion:
        case = self.kernel_repository.get_case(case_id)
        self._assert_actor_is_not_subject(created_by, subject_id)
        self._assert_sensitivity_allowed(case.sensitivity, sensitivity)
        if case.owner_id != owner_id:
            raise PermissionBoundaryError("Permission owner must match the Kernel case owner")

        grant = PermissionGrantVersion(
            grant_id=uuid4(),
            case_id=case_id,
            blueprint_id=blueprint_id,
            blueprint_version_id=blueprint_version_id,
            blueprint_fingerprint=blueprint_fingerprint,
            subject_id=subject_id,
            owner_id=owner_id,
            created_by=created_by,
            tool_name=tool_name,
            resource_prefixes=resource_prefixes,
            allowed_actions=allowed_actions,
            denied_actions=denied_actions,
            approval_required_actions=approval_required_actions,
            sensitivity=sensitivity,
            version=1,
            status=GrantStatus.DRAFT,
            reason=reason,
            review_at=review_at,
            expires_at=expires_at,
        )
        stored = self._append_version(grant)
        self._record_event(
            stored,
            PermissionEventType.GRANT_CREATED,
            created_by,
            {"permission_fingerprint": stored.permission_fingerprint},
        )
        return stored

    def activate_grant(
        self,
        *,
        grant_id: UUID,
        approver_id: UUID,
        rationale: str,
    ) -> tuple[PermissionGrantVersion, PermissionGrantReceipt]:
        latest = self.vigilance_repository.latest_version(grant_id)
        if latest.status != GrantStatus.DRAFT:
            raise PermissionTransitionError("Only a DRAFT grant can be activated")
        self._assert_actor_is_not_subject(approver_id, latest.subject_id)
        if not rationale.strip():
            raise ValueError("Activation rationale is required")
        if latest.sensitivity in {Sensitivity.ORANGE, Sensitivity.RED}:
            if approver_id == latest.owner_id:
                raise PermissionApprovalError(
                    "ORANGE and RED grants require separation between owner and approver"
                )

        activated_at = utc_now()
        active = self._new_version(
            latest,
            created_by=approver_id,
            status=GrantStatus.ACTIVE,
            reason=rationale,
            approved_by=approver_id,
            activated_at=activated_at,
            emergency_disabled=False,
        )
        stored = self._append_version(active)
        receipt = PermissionGrantReceipt(
            grant_id=stored.grant_id,
            grant_version_id=stored.id,
            case_id=stored.case_id,
            blueprint_id=stored.blueprint_id,
            blueprint_version_id=stored.blueprint_version_id,
            blueprint_fingerprint=stored.blueprint_fingerprint,
            permission_fingerprint=stored.permission_fingerprint,
            grant_integrity_hash=stored.integrity_hash,
            approved_by=approver_id,
            activated_at=activated_at,
        )
        stored_receipt = self.vigilance_repository.append_grant_receipt(receipt)
        self.kernel_repository.append_output(
            OutputArtifact(
                case_id=stored.case_id,
                artifact_type="VIGILANCE_PERMISSION_GRANT_RECEIPT",
                owner_id=stored.owner_id,
                content=stored_receipt.to_dict(),
                version=stored.version,
                status=ArtifactStatus.APPROVED,
            )
        )
        self.kernel_repository.append_evidence(
            EvidenceReference(
                case_id=stored.case_id,
                label=f"Vigilance permission grant receipt v{stored.version}",
                uri=f"vigilance://grants/{stored.grant_id}/receipts/{stored_receipt.id}",
                sensitivity=stored.sensitivity,
            )
        )
        self._record_event(
            stored,
            PermissionEventType.GRANT_ACTIVATED,
            approver_id,
            {
                "rationale": rationale.strip(),
                "receipt_id": str(stored_receipt.id),
                "receipt_hash": stored_receipt.receipt_hash,
            },
        )
        return stored, stored_receipt

    def revise_grant(
        self,
        *,
        grant_id: UUID,
        created_by: UUID,
        tool_name: str,
        resource_prefixes: tuple[str, ...],
        allowed_actions: tuple[PermissionAction, ...],
        denied_actions: tuple[PermissionAction, ...],
        approval_required_actions: tuple[PermissionAction, ...],
        reason: str,
        review_at: datetime,
        expires_at: datetime,
        blueprint_version_id: UUID,
        blueprint_fingerprint: str,
    ) -> PermissionGrantVersion:
        latest = self.vigilance_repository.latest_version(grant_id)
        if latest.status in {GrantStatus.REVOKED, GrantStatus.SUPERSEDED}:
            raise PermissionTransitionError("A revoked or superseded grant cannot be revised")
        self._assert_actor_is_not_subject(created_by, latest.subject_id)
        if not reason.strip():
            raise ValueError("Revision reason is required")

        revised = PermissionGrantVersion(
            grant_id=latest.grant_id,
            case_id=latest.case_id,
            blueprint_id=latest.blueprint_id,
            blueprint_version_id=blueprint_version_id,
            blueprint_fingerprint=blueprint_fingerprint,
            subject_id=latest.subject_id,
            owner_id=latest.owner_id,
            created_by=created_by,
            tool_name=tool_name,
            resource_prefixes=resource_prefixes,
            allowed_actions=allowed_actions,
            denied_actions=denied_actions,
            approval_required_actions=approval_required_actions,
            sensitivity=latest.sensitivity,
            version=latest.version + 1,
            status=GrantStatus.DRAFT,
            reason=reason,
            review_at=review_at,
            expires_at=expires_at,
            parent_version_id=latest.id,
        )
        stored = self._append_version(revised)
        self._record_event(
            stored,
            PermissionEventType.GRANT_REVISED,
            created_by,
            {
                "previous_permission_fingerprint": latest.permission_fingerprint,
                "new_permission_fingerprint": stored.permission_fingerprint,
                "reason": reason.strip(),
            },
        )
        return stored

    def request_action_approval(
        self,
        *,
        grant_id: UUID,
        requested_by: UUID,
        action: PermissionAction,
        resource: str,
        justification: str,
        expires_at: datetime,
    ) -> PermissionApprovalRequest:
        latest = self.vigilance_repository.latest_version(grant_id)
        if latest.status != GrantStatus.ACTIVE:
            raise PermissionTransitionError("Action approval requires an ACTIVE grant")
        if requested_by != latest.subject_id:
            raise PermissionBoundaryError(
                "Only the permission subject may request action approval"
            )
        self._validate_action_and_resource(latest, action, resource)
        if action not in latest.approval_required_actions:
            raise PermissionApprovalError(
                "The requested action does not require a separate human approval"
            )

        request = PermissionApprovalRequest(
            grant_id=latest.grant_id,
            grant_version_id=latest.id,
            grant_permission_fingerprint=latest.permission_fingerprint,
            case_id=latest.case_id,
            subject_id=latest.subject_id,
            requested_by=requested_by,
            action=action,
            resource=resource,
            justification=justification,
            expires_at=expires_at,
        )
        stored = self.vigilance_repository.append_request(request)
        self._record_event(
            latest,
            PermissionEventType.APPROVAL_REQUESTED,
            requested_by,
            {
                "request_id": str(stored.id),
                "action": action.value,
                "resource": resource.strip(),
            },
        )
        return stored

    def decide_action_request(
        self,
        *,
        request_id: UUID,
        approver_id: UUID,
        decision: ApprovalDecision,
        rationale: str,
    ) -> PermissionApprovalRecord:
        request = self.vigilance_repository.get_request(request_id)
        latest = self.vigilance_repository.latest_version(request.grant_id)
        if latest.id != request.grant_version_id:
            raise StalePermissionError("Approval request belongs to an older grant version")
        if latest.permission_fingerprint != request.grant_permission_fingerprint:
            raise StalePermissionError("Permission fingerprint changed after the request")
        self._assert_actor_is_not_subject(approver_id, latest.subject_id)
        if approver_id == request.requested_by:
            raise PermissionApprovalError("A requester cannot approve its own action")
        if self.vigilance_repository.decisions_for_request(request_id):
            raise PermissionApprovalError("The action request already has a decision")
        if utc_now() >= request.expires_at:
            raise PermissionApprovalError("The action request has expired")
        if not rationale.strip():
            raise ValueError("Approval decision rationale is required")

        record = PermissionApprovalRecord(
            request_id=request.id,
            grant_id=request.grant_id,
            grant_version_id=request.grant_version_id,
            grant_permission_fingerprint=request.grant_permission_fingerprint,
            approver_id=approver_id,
            decision=decision,
            rationale=rationale,
        )
        stored = self.vigilance_repository.append_approval_record(record)
        self._record_event(
            latest,
            PermissionEventType.APPROVAL_DECIDED,
            approver_id,
            {
                "request_id": str(request.id),
                "decision_id": str(stored.id),
                "decision": decision.value,
                "rationale": rationale.strip(),
            },
        )
        return stored

    def authorize_action(
        self,
        *,
        grant_id: UUID,
        subject_id: UUID,
        action: PermissionAction,
        resource: str,
        evaluated_by: UUID,
    ) -> ActionAuthorizationReceipt:
        latest = self.vigilance_repository.latest_version(grant_id)
        outcome, reason, request_id, decision_id = self._evaluate(
            latest=latest,
            subject_id=subject_id,
            action=action,
            resource=resource,
        )
        receipt = ActionAuthorizationReceipt(
            grant_id=latest.grant_id,
            grant_version_id=latest.id,
            grant_permission_fingerprint=latest.permission_fingerprint,
            case_id=latest.case_id,
            subject_id=subject_id,
            action=action,
            resource=resource,
            outcome=outcome,
            reason=reason,
            evaluated_by=evaluated_by,
            approval_request_id=request_id,
            approval_record_id=decision_id,
        )
        stored = self.vigilance_repository.append_authorization_receipt(receipt)
        self.kernel_repository.append_evidence(
            EvidenceReference(
                case_id=latest.case_id,
                label=f"Vigilance authorization {outcome.value}: {action.value}",
                uri=f"vigilance://authorizations/{stored.id}",
                sensitivity=latest.sensitivity,
            )
        )
        self._record_event(
            latest,
            PermissionEventType.AUTHORIZATION_EVALUATED,
            evaluated_by,
            {
                "authorization_receipt_id": str(stored.id),
                "outcome": outcome.value,
                "action": action.value,
                "resource": resource.strip(),
                "reason": reason,
            },
        )
        return stored

    def record_action_execution(
        self,
        *,
        authorization: ActionAuthorizationReceipt,
        recorded_by: UUID,
        execution_reference: str,
    ) -> PermissionEvent:
        if authorization.outcome != AuthorizationOutcome.ALLOWED:
            raise PermissionBoundaryError("Only an ALLOWED authorization can be recorded")
        if not execution_reference.strip():
            raise ValueError("Execution reference is required")
        latest = self.vigilance_repository.latest_version(authorization.grant_id)
        if latest.id != authorization.grant_version_id:
            raise StalePermissionError("Authorization belongs to an older grant version")
        event = self._record_event(
            latest,
            PermissionEventType.ACTION_RECORDED,
            recorded_by,
            {
                "authorization_receipt_id": str(authorization.id),
                "authorization_receipt_hash": authorization.receipt_hash,
                "execution_reference": execution_reference.strip(),
                "note": "Vigilance records evidence but does not execute the action",
            },
        )
        return event

    def emergency_disable(
        self,
        *,
        grant_id: UUID,
        disabled_by: UUID,
        reason: str,
    ) -> PermissionGrantVersion:
        latest = self.vigilance_repository.latest_version(grant_id)
        if latest.status in {GrantStatus.REVOKED, GrantStatus.SUPERSEDED}:
            raise PermissionTransitionError("The grant is already permanently inactive")
        self._assert_actor_is_not_subject(disabled_by, latest.subject_id)
        if not reason.strip():
            raise ValueError("Emergency disable reason is required")

        disabled = self._new_version(
            latest,
            created_by=disabled_by,
            status=GrantStatus.SUSPENDED,
            reason=reason,
            approved_by=None,
            activated_at=None,
            emergency_disabled=True,
        )
        stored = self._append_version(disabled)
        self._record_event(
            stored,
            PermissionEventType.EMERGENCY_DISABLED,
            disabled_by,
            {"reason": reason.strip()},
        )
        return stored

    def revoke_grant(
        self,
        *,
        grant_id: UUID,
        revoked_by: UUID,
        reason: str,
    ) -> PermissionGrantVersion:
        latest = self.vigilance_repository.latest_version(grant_id)
        if latest.status == GrantStatus.REVOKED:
            raise PermissionTransitionError("The grant is already revoked")
        self._assert_actor_is_not_subject(revoked_by, latest.subject_id)
        if not reason.strip():
            raise ValueError("Revocation reason is required")
        revoked = self._new_version(
            latest,
            created_by=revoked_by,
            status=GrantStatus.REVOKED,
            reason=reason,
            approved_by=None,
            activated_at=None,
            emergency_disabled=False,
        )
        stored = self._append_version(revoked)
        self._record_event(
            stored,
            PermissionEventType.GRANT_REVOKED,
            revoked_by,
            {"reason": reason.strip()},
        )
        return stored

    def _evaluate(
        self,
        *,
        latest: PermissionGrantVersion,
        subject_id: UUID,
        action: PermissionAction,
        resource: str,
    ) -> tuple[AuthorizationOutcome, str, UUID | None, UUID | None]:
        if subject_id != latest.subject_id:
            return AuthorizationOutcome.DENIED, "Subject does not match the grant", None, None
        if latest.emergency_disabled:
            return (
                AuthorizationOutcome.EMERGENCY_BLOCK,
                "Emergency disable is active",
                None,
                None,
            )
        if latest.status != GrantStatus.ACTIVE:
            return AuthorizationOutcome.DENIED, f"Grant status is {latest.status.value}", None, None
        now = utc_now()
        if now >= latest.expires_at:
            return AuthorizationOutcome.DENIED, "Permission grant has expired", None, None
        if now >= latest.review_at:
            return AuthorizationOutcome.DENIED, "Permission review is overdue", None, None
        try:
            self._validate_action_and_resource(latest, action, resource)
        except PermissionBoundaryError as exc:
            return AuthorizationOutcome.DENIED, str(exc), None, None

        if action not in latest.approval_required_actions:
            return AuthorizationOutcome.ALLOWED, "Explicit least-privilege grant permits action", None, None

        matching_requests = [
            request
            for request in self.vigilance_repository.requests_for_grant(latest.grant_id)
            if request.grant_version_id == latest.id
            and request.grant_permission_fingerprint == latest.permission_fingerprint
            and request.action == action
            and request.resource.strip() == resource.strip()
            and now < request.expires_at
        ]
        if not matching_requests:
            return (
                AuthorizationOutcome.PENDING_APPROVAL,
                "Named human approval is required",
                None,
                None,
            )

        request = matching_requests[-1]
        decisions = self.vigilance_repository.decisions_for_request(request.id)
        if not decisions:
            return (
                AuthorizationOutcome.PENDING_APPROVAL,
                "Approval request is pending",
                request.id,
                None,
            )
        decision = decisions[-1]
        if decision.decision == ApprovalDecision.DENY:
            return (
                AuthorizationOutcome.DENIED,
                "Named human approver denied the action",
                request.id,
                decision.id,
            )
        return (
            AuthorizationOutcome.ALLOWED,
            "Exact action and resource were approved by a named human",
            request.id,
            decision.id,
        )

    @staticmethod
    def _validate_action_and_resource(
        grant: PermissionGrantVersion,
        action: PermissionAction,
        resource: str,
    ) -> None:
        cleaned_resource = resource.strip()
        if not cleaned_resource:
            raise PermissionBoundaryError("Resource is required")
        if action in grant.denied_actions:
            raise PermissionBoundaryError(f"Action {action.value} is explicitly denied")
        if action not in grant.allowed_actions:
            raise PermissionBoundaryError(f"Action {action.value} is not explicitly allowed")
        if not any(cleaned_resource.startswith(prefix) for prefix in grant.resource_prefixes):
            raise PermissionBoundaryError("Resource is outside the explicit grant scope")

    def _append_version(self, grant: PermissionGrantVersion) -> PermissionGrantVersion:
        stored = self.vigilance_repository.append_version(grant)
        self.kernel_repository.append_output(
            OutputArtifact(
                case_id=stored.case_id,
                artifact_type="VIGILANCE_PERMISSION_GRANT",
                owner_id=stored.owner_id,
                content=stored.to_dict(),
                version=stored.version,
                status=(
                    ArtifactStatus.APPROVED
                    if stored.status == GrantStatus.ACTIVE
                    else ArtifactStatus.REVIEW
                    if stored.status == GrantStatus.DRAFT
                    else ArtifactStatus.REJECTED
                ),
            )
        )
        self.kernel_repository.append_evidence(
            EvidenceReference(
                case_id=stored.case_id,
                label=f"Vigilance permission grant {stored.status.value} v{stored.version}",
                uri=f"vigilance://grants/{stored.grant_id}/versions/{stored.version}",
                sensitivity=stored.sensitivity,
            )
        )
        return stored

    def _record_event(
        self,
        grant: PermissionGrantVersion,
        event_type: PermissionEventType,
        actor_id: UUID,
        details: dict[str, object],
    ) -> PermissionEvent:
        event = PermissionEvent(
            case_id=grant.case_id,
            grant_id=grant.grant_id,
            event_type=event_type,
            actor_id=actor_id,
            details=dict(details),
        )
        return self.vigilance_repository.append_event(event)

    @staticmethod
    def _new_version(
        latest: PermissionGrantVersion,
        *,
        created_by: UUID,
        status: GrantStatus,
        reason: str,
        approved_by: UUID | None,
        activated_at: datetime | None,
        emergency_disabled: bool,
    ) -> PermissionGrantVersion:
        return replace(
            latest,
            id=uuid4(),
            created_at=utc_now(),
            version=latest.version + 1,
            parent_version_id=latest.id,
            created_by=created_by,
            status=status,
            reason=reason,
            approved_by=approved_by,
            activated_at=activated_at,
            emergency_disabled=emergency_disabled,
        )

    @staticmethod
    def _assert_actor_is_not_subject(actor_id: UUID, subject_id: UUID) -> None:
        if actor_id == subject_id:
            raise PermissionBoundaryError(
                "An agent cannot issue, approve, revise, suspend, or revoke its own permissions"
            )

    @staticmethod
    def _assert_sensitivity_allowed(
        case_sensitivity: Sensitivity,
        grant_sensitivity: Sensitivity,
    ) -> None:
        order = {
            Sensitivity.GREEN: 0,
            Sensitivity.ORANGE: 1,
            Sensitivity.RED: 2,
        }
        if order[grant_sensitivity] > order[case_sensitivity]:
            raise PermissionBoundaryError(
                "Grant sensitivity cannot exceed the Kernel case sensitivity"
            )

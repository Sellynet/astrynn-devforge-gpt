from uuid import uuid4

import pytest

from astrynn_devforge.aegis import (
    AegisClearanceService,
    AIUseCase,
    ClearanceDecision,
    RiskScores,
    SpecialistReviewTrigger,
)
from astrynn_devforge.kernel import (
    CaseStatus,
    InMemoryKernelRepository,
    KernelService,
    Sensitivity,
)


def build_scores(**overrides: int) -> RiskScores:
    values = {
        "data": 0,
        "permissions": 0,
        "autonomy": 0,
        "impact": 0,
        "traceability": 0,
        "human_oversight": 0,
        "external_dependency": 0,
        "adversarial_robustness": 0,
        "incident_readiness": 0,
    }
    values.update(overrides)
    return RiskScores(**values)


def build_use_case(
    *,
    scores: RiskScores,
    case_id=None,
    specialist_triggers=(),
    critical_blockers=(),
) -> AIUseCase:
    return AIUseCase(
        case_id=case_id or uuid4(),
        organization_id=uuid4(),
        owner_id=uuid4(),
        title="Customer support copilot",
        purpose="Prepare draft answers for human review",
        sector="professional_services",
        scores=scores,
        data_categories=("customer_questions",),
        systems=("knowledge_base",),
        users=("support_team",),
        requested_actions=("draft_response",),
        providers=("external_llm",),
        specialist_triggers=specialist_triggers,
        critical_blockers=critical_blockers,
    )


def test_scores_require_integers_between_zero_and_five() -> None:
    with pytest.raises(ValueError):
        build_scores(data=6)

    with pytest.raises(ValueError):
        build_scores(permissions=-1)

    with pytest.raises(TypeError):
        build_scores(autonomy=True)


def test_low_risk_case_is_apto() -> None:
    use_case = build_use_case(scores=build_scores(data=1, external_dependency=1))

    package = AegisClearanceService().evaluate(use_case)

    assert package.result.decision == ClearanceDecision.APTO
    assert package.result.total_score == 2
    assert package.result.conditions == ()


def test_medium_risk_case_requires_controls() -> None:
    use_case = build_use_case(
        scores=build_scores(
            data=2,
            permissions=2,
            autonomy=2,
            impact=2,
            traceability=2,
            human_oversight=2,
        )
    )

    package = AegisClearanceService().evaluate(use_case)

    assert package.result.decision == ClearanceDecision.APTO_CON_CONTROLES
    assert package.result.total_score == 12
    assert package.result.guardrails
    assert package.result.conditions


def test_high_aggregate_risk_is_not_ready() -> None:
    use_case = build_use_case(
        scores=build_scores(
            data=3,
            permissions=3,
            autonomy=3,
            impact=3,
            traceability=3,
            human_oversight=3,
            external_dependency=3,
            adversarial_robustness=3,
            incident_readiness=3,
        )
    )

    package = AegisClearanceService().evaluate(use_case)

    assert package.result.decision == ClearanceDecision.NO_APTO_TODAVIA
    assert package.result.total_score == 27
    assert "Redesign" in package.result.conditions[0]


def test_specialist_trigger_overrides_low_score() -> None:
    use_case = build_use_case(
        scores=build_scores(),
        specialist_triggers=(SpecialistReviewTrigger.HEALTH,),
    )

    package = AegisClearanceService().evaluate(use_case)

    assert package.result.decision == ClearanceDecision.REQUIERE_REVISION_ESPECIALIZADA
    assert package.result.specialist_triggers == (SpecialistReviewTrigger.HEALTH,)


def test_maximum_critical_dimension_blocks_deployment() -> None:
    use_case = build_use_case(scores=build_scores(permissions=5))

    package = AegisClearanceService().evaluate(use_case)

    assert package.result.total_score == 5
    assert package.result.decision == ClearanceDecision.NO_APTO_TODAVIA


def test_concentrated_high_risk_requires_controls_even_with_low_total() -> None:
    use_case = build_use_case(scores=build_scores(external_dependency=4))

    package = AegisClearanceService().evaluate(use_case)

    assert package.result.total_score == 4
    assert package.result.decision == ClearanceDecision.APTO_CON_CONTROLES


def test_input_fingerprint_is_deterministic() -> None:
    fixed_case_id = uuid4()
    first = build_use_case(scores=build_scores(data=2), case_id=fixed_case_id)
    second = AIUseCase(
        case_id=first.case_id,
        organization_id=first.organization_id,
        owner_id=first.owner_id,
        title=first.title,
        purpose=first.purpose,
        sector=first.sector,
        scores=first.scores,
        data_categories=first.data_categories,
        systems=first.systems,
        users=first.users,
        requested_actions=first.requested_actions,
        providers=first.providers,
    )

    assert first.fingerprint() == second.fingerprint()


def test_record_creates_review_artifact_and_evidence_without_activation() -> None:
    repository = InMemoryKernelRepository()
    kernel = KernelService(repository)
    owner_id = uuid4()
    organization_id = uuid4()
    case = kernel.create_case(
        title="Aegis pilot",
        description="Evaluate a controlled use case",
        owner_id=owner_id,
        organization_id=organization_id,
        sensitivity=Sensitivity.ORANGE,
        actor_id=owner_id,
    )
    use_case = AIUseCase(
        case_id=case.id,
        organization_id=organization_id,
        owner_id=owner_id,
        title="Document summarizer",
        purpose="Draft internal summaries for human review",
        sector="professional_services",
        scores=build_scores(data=2, permissions=2, traceability=2),
    )
    service = AegisClearanceService()

    package = service.evaluate(use_case)
    output, evidence = service.record(
        package=package,
        repository=repository,
        owner_id=owner_id,
    )

    assert output.artifact_type == "AEGIS_CLEARANCE_REPORT"
    assert evidence.uri.startswith("aegis://clearance/")
    assert len(repository.outputs_for_case(case.id)) == 1
    assert len(repository.evidence_for_case(case.id)) == 1
    assert repository.get_case(case.id).status == CaseStatus.DRAFT

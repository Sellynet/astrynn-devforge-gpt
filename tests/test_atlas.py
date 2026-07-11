from uuid import uuid4

import pytest

from astrynn_devforge.atlas import (
    AtlasCaseInput,
    AtlasRisk,
    AtlasScenario,
    AtlasSignal,
    AtlasSource,
    AtlasStakeholder,
    AtlasValidationError,
    OrbynAtlasService,
    RiskLevel,
    ScenarioType,
    SourceKind,
    StatementType,
)
from astrynn_devforge.kernel import (
    ArtifactStatus,
    CaseStatus,
    InMemoryKernelRepository,
    KernelService,
    Sensitivity,
)


def build_kernel_case(*, sensitivity: Sensitivity = Sensitivity.GREEN):
    repository = InMemoryKernelRepository()
    kernel = KernelService(repository)
    owner_id = uuid4()
    organization_id = uuid4()
    case = kernel.create_case(
        title="Orbyn Isthmus logistics pilot",
        description="Decision-support case using non-critical public data",
        owner_id=owner_id,
        organization_id=organization_id,
        sensitivity=sensitivity,
        actor_id=owner_id,
    )
    return repository, case, owner_id, organization_id


def build_atlas_payload(*, sensitivity: Sensitivity = Sensitivity.GREEN):
    repository, case, owner_id, organization_id = build_kernel_case(
        sensitivity=sensitivity
    )
    case_input = AtlasCaseInput(
        case_id=case.id,
        organization_id=organization_id,
        owner_id=owner_id,
        title="Panama logistics resilience",
        problem="Assess congestion signals and operational response options",
        sector="Logistics",
        country="Panama",
        horizon_days=90,
        asset="Public logistics ecosystem",
    )
    source = AtlasSource(
        case_id=case.id,
        title="Public port activity bulletin",
        kind=SourceKind.PUBLIC,
        confidence=85,
        sensitivity=sensitivity,
        uri="https://example.invalid/public-bulletin",
    )
    signal = AtlasSignal(
        case_id=case.id,
        title="Sustained congestion signal",
        observation="Public bulletins show a sustained increase in waiting times.",
        source_ids=(source.id,),
        confidence=80,
    )
    risk = AtlasRisk(
        case_id=case.id,
        title="Operational delay concentration",
        description="A prolonged concentration of delays may affect planning reliability.",
        probability=4,
        impact=4,
        related_signal_ids=(signal.id,),
        mitigation="Introduce thresholds, alternate routing analysis and a human review gate.",
    )
    stakeholder = AtlasStakeholder(
        case_id=case.id,
        name="Logistics operations lead",
        role="Decision owner",
        influence=5,
        exposure=4,
        interests=("Continuity", "Cost control", "Traceable decisions"),
    )
    scenarios = tuple(
        AtlasScenario(
            case_id=case.id,
            scenario_type=scenario_type,
            title=f"{scenario_type.value.title()} scenario",
            narrative=f"Controlled narrative for the {scenario_type.value} case.",
            assumptions=(f"Assumption for {scenario_type.value}",),
            early_indicators=(f"Indicator for {scenario_type.value}",),
            response_options=(f"Response for {scenario_type.value}",),
        )
        for scenario_type in ScenarioType
    )
    return (
        repository,
        case,
        owner_id,
        case_input,
        (source,),
        (signal,),
        (risk,),
        (stakeholder,),
        scenarios,
    )


def test_builds_traceable_briefing_with_four_scenarios() -> None:
    (
        repository,
        case,
        _owner_id,
        case_input,
        sources,
        signals,
        risks,
        stakeholders,
        scenarios,
    ) = build_atlas_payload()
    package = OrbynAtlasService(repository).build_package(
        case_input=case_input,
        sources=sources,
        signals=signals,
        risks=risks,
        stakeholders=stakeholders,
        scenarios=scenarios,
    )

    assert package.briefing.case_id == case.id
    assert package.briefing.facts[0].statement_type == StatementType.FACT
    assert package.briefing.facts[0].source_ids == (sources[0].id,)
    assert package.briefing.inferences[0].statement_type == StatementType.INFERENCE
    assert package.briefing.recommendations[0].statement_type == (
        StatementType.RECOMMENDATION
    )
    assert package.receipt.scenario_types == (
        ScenarioType.BASE,
        ScenarioType.ADVERSE,
        ScenarioType.OPTIMISTIC,
        ScenarioType.STRESS,
    )
    assert risks[0].level == RiskLevel.HIGH


def test_recording_briefing_does_not_activate_kernel_case() -> None:
    (
        repository,
        case,
        owner_id,
        case_input,
        sources,
        signals,
        risks,
        stakeholders,
        scenarios,
    ) = build_atlas_payload()
    service = OrbynAtlasService(repository)
    package = service.build_package(
        case_input=case_input,
        sources=sources,
        signals=signals,
        risks=risks,
        stakeholders=stakeholders,
        scenarios=scenarios,
    )
    output, evidence = service.record_package(
        package=package,
        owner_id=owner_id,
        sensitivity=Sensitivity.GREEN,
    )

    assert output.status == ArtifactStatus.REVIEW
    assert evidence.uri.startswith("atlas://briefings/")
    assert repository.get_case(case.id).status == CaseStatus.DRAFT
    assert repository.outputs_for_case(case.id) == (output,)
    assert repository.evidence_for_case(case.id) == (evidence,)


def test_fingerprint_is_reproducible_for_same_payload() -> None:
    (
        repository,
        _case,
        _owner_id,
        case_input,
        sources,
        signals,
        risks,
        stakeholders,
        scenarios,
    ) = build_atlas_payload()
    service = OrbynAtlasService(repository)

    first = service.build_package(
        case_input=case_input,
        sources=sources,
        signals=signals,
        risks=risks,
        stakeholders=stakeholders,
        scenarios=scenarios,
    )
    second = service.build_package(
        case_input=case_input,
        sources=sources,
        signals=signals,
        risks=risks,
        stakeholders=stakeholders,
        scenarios=scenarios,
    )

    assert first.briefing.input_fingerprint == second.briefing.input_fingerprint
    assert first.receipt.input_fingerprint == second.receipt.input_fingerprint


def test_requires_exactly_one_scenario_of_each_type() -> None:
    (
        repository,
        _case,
        _owner_id,
        case_input,
        sources,
        signals,
        risks,
        stakeholders,
        scenarios,
    ) = build_atlas_payload()

    with pytest.raises(AtlasValidationError, match="Exactly one"):
        OrbynAtlasService(repository).build_package(
            case_input=case_input,
            sources=sources,
            signals=signals,
            risks=risks,
            stakeholders=stakeholders,
            scenarios=scenarios[:-1],
        )


def test_rejects_source_more_sensitive_than_kernel_case() -> None:
    (
        repository,
        case,
        _owner_id,
        case_input,
        _sources,
        signals,
        risks,
        stakeholders,
        scenarios,
    ) = build_atlas_payload()
    red_source = AtlasSource(
        case_id=case.id,
        title="Restricted source",
        kind=SourceKind.INTERNAL_APPROVED,
        confidence=90,
        sensitivity=Sensitivity.RED,
    )
    aligned_signal = AtlasSignal(
        case_id=case.id,
        title=signals[0].title,
        observation=signals[0].observation,
        source_ids=(red_source.id,),
        confidence=signals[0].confidence,
        id=signals[0].id,
    )

    with pytest.raises(AtlasValidationError, match="sensitivity"):
        OrbynAtlasService(repository).build_package(
            case_input=case_input,
            sources=(red_source,),
            signals=(aligned_signal,),
            risks=risks,
            stakeholders=stakeholders,
            scenarios=scenarios,
        )


def test_rejects_unknown_source_reference() -> None:
    (
        repository,
        case,
        _owner_id,
        case_input,
        sources,
        _signals,
        risks,
        stakeholders,
        scenarios,
    ) = build_atlas_payload()
    unknown_signal = AtlasSignal(
        case_id=case.id,
        title="Untraceable signal",
        observation="This statement lacks a registered source.",
        source_ids=(uuid4(),),
        confidence=50,
    )
    aligned_risk = AtlasRisk(
        case_id=case.id,
        title=risks[0].title,
        description=risks[0].description,
        probability=risks[0].probability,
        impact=risks[0].impact,
        related_signal_ids=(unknown_signal.id,),
    )

    with pytest.raises(AtlasValidationError, match="unknown sources"):
        OrbynAtlasService(repository).build_package(
            case_input=case_input,
            sources=sources,
            signals=(unknown_signal,),
            risks=(aligned_risk,),
            stakeholders=stakeholders,
            scenarios=scenarios,
        )


def test_source_confidence_must_be_valid_percentage() -> None:
    repository, case, _owner_id, _organization_id = build_kernel_case()
    del repository

    with pytest.raises(ValueError, match="between 0 and 100"):
        AtlasSource(
            case_id=case.id,
            title="Invalid source",
            kind=SourceKind.PUBLIC,
            confidence=101,
            sensitivity=Sensitivity.GREEN,
        )

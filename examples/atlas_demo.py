from __future__ import annotations

import json
from uuid import uuid4

from astrynn_devforge.atlas import (
    AtlasCaseInput,
    AtlasRisk,
    AtlasScenario,
    AtlasSignal,
    AtlasSource,
    AtlasStakeholder,
    OrbynAtlasService,
    ScenarioType,
    SourceKind,
)
from astrynn_devforge.kernel import InMemoryKernelRepository, KernelService, Sensitivity


def main() -> None:
    repository = InMemoryKernelRepository()
    kernel = KernelService(repository)
    owner_id = uuid4()
    organization_id = uuid4()
    case = kernel.create_case(
        title="Orbyn Isthmus public logistics demo",
        description="Synthetic and public-data decision-support demonstration",
        owner_id=owner_id,
        organization_id=organization_id,
        sensitivity=Sensitivity.GREEN,
        actor_id=owner_id,
    )

    case_input = AtlasCaseInput(
        case_id=case.id,
        organization_id=organization_id,
        owner_id=owner_id,
        title="Panama logistics resilience demo",
        problem="Assess a public congestion signal and document response options",
        sector="Logistics",
        country="Panama",
        horizon_days=90,
        asset="Public logistics ecosystem",
    )
    source = AtlasSource(
        case_id=case.id,
        title="Synthetic public bulletin",
        kind=SourceKind.SYNTHETIC,
        confidence=80,
        sensitivity=Sensitivity.GREEN,
        notes="Demonstration data only",
    )
    signal = AtlasSignal(
        case_id=case.id,
        title="Waiting-time increase",
        observation="The synthetic bulletin reports a sustained waiting-time increase.",
        source_ids=(source.id,),
        confidence=75,
    )
    risk = AtlasRisk(
        case_id=case.id,
        title="Planning reliability deterioration",
        description="Sustained delay concentration may reduce planning reliability.",
        probability=4,
        impact=4,
        related_signal_ids=(signal.id,),
        mitigation="Introduce thresholds and require human review before operational changes.",
    )
    stakeholder = AtlasStakeholder(
        case_id=case.id,
        name="Operations lead",
        role="Human decision owner",
        influence=5,
        exposure=4,
        interests=("Continuity", "Cost", "Evidence"),
    )
    scenarios = tuple(
        AtlasScenario(
            case_id=case.id,
            scenario_type=scenario_type,
            title=f"{scenario_type.value.title()} scenario",
            narrative=f"Synthetic narrative for {scenario_type.value} conditions.",
            assumptions=(f"Synthetic assumption for {scenario_type.value}",),
            early_indicators=(f"Synthetic indicator for {scenario_type.value}",),
            response_options=(f"Human-reviewed response for {scenario_type.value}",),
        )
        for scenario_type in ScenarioType
    )

    atlas = OrbynAtlasService(repository)
    package = atlas.build_package(
        case_input=case_input,
        sources=(source,),
        signals=(signal,),
        risks=(risk,),
        stakeholders=(stakeholder,),
        scenarios=scenarios,
    )
    output, evidence = atlas.record_package(
        package=package,
        owner_id=owner_id,
        sensitivity=Sensitivity.GREEN,
    )

    result = {
        "briefing": package.briefing.to_dict(),
        "proof_receipt": package.receipt.to_dict(),
        "kernel_output_status": output.status.value,
        "evidence_uri": evidence.uri,
        "kernel_case_status": repository.get_case(case.id).status.value,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

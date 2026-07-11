from __future__ import annotations

from collections.abc import Iterable
from uuid import UUID

from astrynn_devforge.kernel import (
    ArtifactStatus,
    EvidenceReference,
    InMemoryKernelRepository,
    OutputArtifact,
    Sensitivity,
)

from .enums import RiskLevel, ScenarioType, StatementType
from .models import (
    AtlasBriefing,
    AtlasCaseInput,
    AtlasPackage,
    AtlasProofReceipt,
    AtlasRisk,
    AtlasScenario,
    AtlasSignal,
    AtlasSource,
    AtlasStakeholder,
    AtlasStatement,
    fingerprint_payload,
)


class AtlasValidationError(ValueError):
    pass


_SCENARIO_ORDER = {
    ScenarioType.BASE: 0,
    ScenarioType.ADVERSE: 1,
    ScenarioType.OPTIMISTIC: 2,
    ScenarioType.STRESS: 3,
}

_SENSITIVITY_ORDER = {
    Sensitivity.GREEN: 0,
    Sensitivity.ORANGE: 1,
    Sensitivity.RED: 2,
}


class OrbynAtlasService:
    """Builds traceable operational briefings without taking external action."""

    def __init__(self, repository: InMemoryKernelRepository) -> None:
        self.repository = repository

    def build_package(
        self,
        *,
        case_input: AtlasCaseInput,
        sources: tuple[AtlasSource, ...],
        signals: tuple[AtlasSignal, ...],
        risks: tuple[AtlasRisk, ...],
        stakeholders: tuple[AtlasStakeholder, ...],
        scenarios: tuple[AtlasScenario, ...],
    ) -> AtlasPackage:
        kernel_case = self.repository.get_case(case_input.case_id)
        self._validate_case_alignment(
            case_id=case_input.case_id,
            sources=sources,
            signals=signals,
            risks=risks,
            stakeholders=stakeholders,
            scenarios=scenarios,
        )
        self._validate_source_sensitivity(kernel_case.sensitivity, sources)
        self._validate_references(sources=sources, signals=signals, risks=risks)
        ordered_scenarios = self._validate_and_order_scenarios(scenarios)

        ordered_risks = tuple(
            sorted(risks, key=lambda item: (-item.severity, item.title.casefold()))
        )
        fingerprint = self._fingerprint(
            case_input=case_input,
            sources=sources,
            signals=signals,
            risks=ordered_risks,
            stakeholders=stakeholders,
            scenarios=ordered_scenarios,
        )

        facts = tuple(
            AtlasStatement(
                statement_type=StatementType.FACT,
                text=signal.observation,
                source_ids=signal.source_ids,
                rationale=(
                    f"Señal registrada con confianza {signal.confidence}%: "
                    f"{signal.title}."
                ),
            )
            for signal in sorted(signals, key=lambda item: item.title.casefold())
        )
        inferences = tuple(self._risk_inference(risk) for risk in ordered_risks[:5])
        assumptions = self._assumption_statements(ordered_scenarios)
        recommendations = tuple(
            self._risk_recommendation(risk) for risk in ordered_risks[:5]
        )

        critical_count = sum(
            1 for risk in ordered_risks if risk.level == RiskLevel.CRITICAL
        )
        high_count = sum(1 for risk in ordered_risks if risk.level == RiskLevel.HIGH)
        executive_summary = (
            f"El caso '{case_input.title.strip()}' analiza {len(signals)} señales, "
            f"{len(ordered_risks)} riesgos y {len(stakeholders)} actores en un horizonte "
            f"de {case_input.horizon_days} días. Se identifican {critical_count} riesgos "
            f"críticos y {high_count} riesgos altos. El resultado es apoyo a decisión: "
            "no ejecuta acciones, no controla infraestructura y requiere validación humana."
        )

        briefing = AtlasBriefing(
            case_id=case_input.case_id,
            title=f"Orbyn Atlas Briefing · {case_input.title.strip()}",
            executive_summary=executive_summary,
            facts=facts,
            inferences=inferences,
            assumptions=assumptions,
            recommendations=recommendations,
            top_risk_ids=tuple(item.id for item in ordered_risks[:5]),
            scenario_ids=tuple(item.id for item in ordered_scenarios),
            stakeholder_ids=tuple(
                item.id
                for item in sorted(
                    stakeholders,
                    key=lambda actor: (-actor.influence, -actor.exposure, actor.name),
                )
            ),
            source_ids=tuple(item.id for item in sorted(sources, key=lambda x: x.title)),
            input_fingerprint=fingerprint,
        )
        receipt = AtlasProofReceipt(
            case_id=case_input.case_id,
            briefing_id=briefing.id,
            input_fingerprint=fingerprint,
            source_ids=briefing.source_ids,
            risk_ids=tuple(item.id for item in ordered_risks),
            scenario_types=tuple(item.scenario_type for item in ordered_scenarios),
        )
        return AtlasPackage(briefing=briefing, receipt=receipt)

    def record_package(
        self,
        *,
        package: AtlasPackage,
        owner_id: UUID,
        sensitivity: Sensitivity,
    ) -> tuple[OutputArtifact, EvidenceReference]:
        self.repository.get_case(package.briefing.case_id)
        output = OutputArtifact(
            case_id=package.briefing.case_id,
            artifact_type="ORBYN_ATLAS_BRIEFING",
            owner_id=owner_id,
            content={
                "briefing": package.briefing.to_dict(),
                "proof_receipt": package.receipt.to_dict(),
            },
            status=ArtifactStatus.REVIEW,
        )
        evidence = EvidenceReference(
            case_id=package.briefing.case_id,
            label="Orbyn Atlas Briefing Proof Receipt",
            uri=f"atlas://briefings/{package.briefing.id}",
            sensitivity=sensitivity,
        )
        self.repository.append_output(output)
        self.repository.append_evidence(evidence)
        return output, evidence

    @staticmethod
    def _validate_case_alignment(
        *,
        case_id: UUID,
        sources: tuple[AtlasSource, ...],
        signals: tuple[AtlasSignal, ...],
        risks: tuple[AtlasRisk, ...],
        stakeholders: tuple[AtlasStakeholder, ...],
        scenarios: tuple[AtlasScenario, ...],
    ) -> None:
        collections: tuple[tuple[str, Iterable[object]], ...] = (
            ("source", sources),
            ("signal", signals),
            ("risk", risks),
            ("stakeholder", stakeholders),
            ("scenario", scenarios),
        )
        for label, items in collections:
            if not tuple(items):
                raise AtlasValidationError(f"At least one {label} is required")
            for item in items:
                if getattr(item, "case_id") != case_id:
                    raise AtlasValidationError(
                        f"{label.capitalize()} belongs to a different Kernel case"
                    )

    @staticmethod
    def _validate_source_sensitivity(
        case_sensitivity: Sensitivity,
        sources: tuple[AtlasSource, ...],
    ) -> None:
        case_rank = _SENSITIVITY_ORDER[case_sensitivity]
        for source in sources:
            if _SENSITIVITY_ORDER[source.sensitivity] > case_rank:
                raise AtlasValidationError(
                    "Kernel case sensitivity must be at least as high as every source"
                )

    @staticmethod
    def _validate_references(
        *,
        sources: tuple[AtlasSource, ...],
        signals: tuple[AtlasSignal, ...],
        risks: tuple[AtlasRisk, ...],
    ) -> None:
        source_ids = {item.id for item in sources}
        signal_ids = {item.id for item in signals}
        for signal in signals:
            unknown = set(signal.source_ids) - source_ids
            if unknown:
                raise AtlasValidationError(
                    f"Signal {signal.id} references unknown sources: {sorted(map(str, unknown))}"
                )
        for risk in risks:
            unknown = set(risk.related_signal_ids) - signal_ids
            if unknown:
                raise AtlasValidationError(
                    f"Risk {risk.id} references unknown signals: {sorted(map(str, unknown))}"
                )

    @staticmethod
    def _validate_and_order_scenarios(
        scenarios: tuple[AtlasScenario, ...],
    ) -> tuple[AtlasScenario, ...]:
        scenario_types = [item.scenario_type for item in scenarios]
        required = set(ScenarioType)
        if len(scenario_types) != len(required) or set(scenario_types) != required:
            raise AtlasValidationError(
                "Exactly one BASE, ADVERSE, OPTIMISTIC and STRESS scenario is required"
            )
        return tuple(sorted(scenarios, key=lambda item: _SCENARIO_ORDER[item.scenario_type]))

    @staticmethod
    def _risk_inference(risk: AtlasRisk) -> AtlasStatement:
        return AtlasStatement(
            statement_type=StatementType.INFERENCE,
            text=(
                f"El riesgo '{risk.title}' requiere atención {risk.level.value.lower()} "
                f"por una severidad calculada de {risk.severity}/25."
            ),
            rationale=(
                f"Probabilidad {risk.probability}/5 multiplicada por impacto "
                f"{risk.impact}/5."
            ),
        )

    @staticmethod
    def _risk_recommendation(risk: AtlasRisk) -> AtlasStatement:
        action = risk.mitigation.strip() or (
            "Definir owner, indicadores tempranos, límites de exposición y respuesta."
        )
        prefix = "Escalar a Aegis antes de cualquier despliegue. " if (
            risk.level == RiskLevel.CRITICAL
        ) else ""
        return AtlasStatement(
            statement_type=StatementType.RECOMMENDATION,
            text=f"{prefix}{action}",
            rationale=f"Mitigación priorizada para el riesgo '{risk.title}'.",
        )

    @staticmethod
    def _assumption_statements(
        scenarios: tuple[AtlasScenario, ...],
    ) -> tuple[AtlasStatement, ...]:
        seen: set[str] = set()
        statements: list[AtlasStatement] = []
        for scenario in scenarios:
            for assumption in scenario.assumptions:
                cleaned = assumption.strip()
                key = cleaned.casefold()
                if key in seen:
                    continue
                seen.add(key)
                statements.append(
                    AtlasStatement(
                        statement_type=StatementType.ASSUMPTION,
                        text=cleaned,
                        rationale=f"Supuesto del escenario {scenario.scenario_type.value}.",
                    )
                )
        return tuple(statements)

    @staticmethod
    def _fingerprint(
        *,
        case_input: AtlasCaseInput,
        sources: tuple[AtlasSource, ...],
        signals: tuple[AtlasSignal, ...],
        risks: tuple[AtlasRisk, ...],
        stakeholders: tuple[AtlasStakeholder, ...],
        scenarios: tuple[AtlasScenario, ...],
    ) -> str:
        payload = {
            "case_input": case_input.canonical_payload(),
            "sources": [
                item.canonical_payload()
                for item in sorted(sources, key=lambda source: str(source.id))
            ],
            "signals": [
                item.canonical_payload()
                for item in sorted(signals, key=lambda signal: str(signal.id))
            ],
            "risks": [
                item.canonical_payload()
                for item in sorted(risks, key=lambda risk: str(risk.id))
            ],
            "stakeholders": [
                item.canonical_payload()
                for item in sorted(stakeholders, key=lambda actor: str(actor.id))
            ],
            "scenarios": [
                item.canonical_payload()
                for item in sorted(
                    scenarios,
                    key=lambda scenario: _SCENARIO_ORDER[scenario.scenario_type],
                )
            ],
            "methodology_version": "ORBYN-ATLAS-0.1",
        }
        return fingerprint_payload(payload)

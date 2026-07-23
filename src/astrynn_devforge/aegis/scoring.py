from __future__ import annotations

from .enums import (
    ClearanceDecision,
    GuardrailPriority,
    RiskDimension,
)
from .models import AIUseCase, GuardrailRecommendation

_CRITICAL_DIMENSIONS = {
    RiskDimension.DATA,
    RiskDimension.PERMISSIONS,
    RiskDimension.AUTONOMY,
    RiskDimension.IMPACT,
    RiskDimension.HUMAN_OVERSIGHT,
    RiskDimension.INCIDENT_READINESS,
}


_GUARDRAIL_LIBRARY: dict[
    RiskDimension, tuple[str, str, str]
] = {
    RiskDimension.DATA: (
        "GR-DATA-01",
        "Definir límites, minimización y clasificación de datos",
        "El caso debe declarar qué datos puede usar, qué datos quedan prohibidos y cómo se retienen o eliminan.",
    ),
    RiskDimension.PERMISSIONS: (
        "GR-PERM-01",
        "Aplicar mínimo privilegio y permisos explícitos",
        "Separar lectura, escritura, envío, borrado y ejecución; prohibir permisos implícitos o heredados.",
    ),
    RiskDimension.AUTONOMY: (
        "GR-AUTO-01",
        "Introducir approval gates y límites de autonomía",
        "Las acciones de impacto deben quedar sujetas a umbrales, revisión humana y capacidad inmediata de parada.",
    ),
    RiskDimension.IMPACT: (
        "GR-IMPACT-01",
        "Limitar alcance, coste y radio de daño",
        "Definir límites operativos, entorno controlado, rollback y criterios de suspensión.",
    ),
    RiskDimension.TRACEABILITY: (
        "GR-TRACE-01",
        "Registrar inputs, outputs, decisiones y versiones",
        "El sistema debe permitir reconstruir qué ocurrió, quién intervino y con qué configuración.",
    ),
    RiskDimension.HUMAN_OVERSIGHT: (
        "GR-HUMAN-01",
        "Nombrar owner, approver y capacidad de override",
        "Debe existir una persona responsable con autoridad para revisar, corregir, pausar o desactivar el sistema.",
    ),
    RiskDimension.EXTERNAL_DEPENDENCY: (
        "GR-VENDOR-01",
        "Controlar proveedores y cambios externos",
        "Documentar proveedores, transferencias, condiciones, fallback y reevaluación ante cambios materiales.",
    ),
    RiskDimension.ADVERSARIAL_ROBUSTNESS: (
        "GR-ARIA-01",
        "Ejecutar pruebas ARIA antes de producción",
        "Probar prompt injection, presión sobre datos, manipulación de rol, deriva de permisos y comportamiento inseguro.",
    ),
    RiskDimension.INCIDENT_READINESS: (
        "GR-INCIDENT-01",
        "Crear playbook de incidente y kill switch",
        "Definir detección, escalado, contención, comunicación, responsables y desactivación segura.",
    ),
}


def determine_decision(use_case: AIUseCase) -> tuple[ClearanceDecision, tuple[str, ...]]:
    scores = use_case.scores.as_dict()
    total = use_case.scores.total
    reasons: list[str] = []

    if use_case.specialist_triggers:
        labels = ", ".join(trigger.value for trigger in use_case.specialist_triggers)
        reasons.append(f"Specialized-review trigger detected: {labels}")
        return ClearanceDecision.REQUIERE_REVISION_ESPECIALIZADA, tuple(reasons)

    if use_case.critical_blockers:
        reasons.append("Critical blockers remain unresolved")
        reasons.extend(use_case.critical_blockers)
        return ClearanceDecision.NO_APTO_TODAVIA, tuple(reasons)

    maximum_critical = tuple(
        dimension.value
        for dimension in _CRITICAL_DIMENSIONS
        if scores[dimension] == 5
    )
    if maximum_critical:
        reasons.append(
            "Maximum exposure in critical dimensions: " + ", ".join(sorted(maximum_critical))
        )
        return ClearanceDecision.NO_APTO_TODAVIA, tuple(reasons)

    concentrated_high_risk = tuple(
        dimension.value for dimension, score in scores.items() if score == 4
    )

    if total <= 10:
        if concentrated_high_risk:
            reasons.append(
                "Low aggregate score but concentrated high exposure requires controls: "
                + ", ".join(sorted(concentrated_high_risk))
            )
            return ClearanceDecision.APTO_CON_CONTROLES, tuple(reasons)
        reasons.append("Aggregate score is within the APTO band (0-10)")
        return ClearanceDecision.APTO, tuple(reasons)

    if total <= 22:
        reasons.append("Aggregate score is within the controlled-deployment band (11-22)")
        return ClearanceDecision.APTO_CON_CONTROLES, tuple(reasons)

    reasons.append("Aggregate score is within the redesign-required band (23-45)")
    return ClearanceDecision.NO_APTO_TODAVIA, tuple(reasons)


def build_guardrails(use_case: AIUseCase) -> tuple[GuardrailRecommendation, ...]:
    recommendations: list[GuardrailRecommendation] = []

    for dimension, score in use_case.scores.as_dict().items():
        if score < 2:
            continue

        if score == 5:
            priority = GuardrailPriority.BLOCKING
        elif score >= 4:
            priority = GuardrailPriority.REQUIRED
        else:
            priority = GuardrailPriority.ADVISORY

        code, title, rationale = _GUARDRAIL_LIBRARY[dimension]
        recommendations.append(
            GuardrailRecommendation(
                code=code,
                title=title,
                rationale=rationale,
                dimensions=(dimension,),
                priority=priority,
            )
        )

    return tuple(recommendations)


def build_conditions(
    decision: ClearanceDecision,
    guardrails: tuple[GuardrailRecommendation, ...],
) -> tuple[str, ...]:
    if decision == ClearanceDecision.APTO:
        return ()

    conditions: list[str] = []

    if decision == ClearanceDecision.REQUIERE_REVISION_ESPECIALIZADA:
        conditions.append(
            "Obtain documented specialist review before any production deployment"
        )
    elif decision == ClearanceDecision.NO_APTO_TODAVIA:
        conditions.append(
            "Redesign the use case, resolve blocking exposures, and submit a new clearance assessment"
        )
    else:
        conditions.append(
            "Implement and verify the listed controls before controlled production activation"
        )

    for guardrail in guardrails:
        conditions.append(f"{guardrail.code}: {guardrail.title}")

    return tuple(dict.fromkeys(conditions))

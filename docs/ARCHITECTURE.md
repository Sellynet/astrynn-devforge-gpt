# Integrated Architecture

## System map

```text
Astrynn Holdings
└── Astrynn Meta-OS / Digital Twin
    ├── Kernel Astrynn
    │   ├── governance
    │   ├── priorities
    │   ├── capital
    │   ├── permissions
    │   ├── memory
    │   ├── decisions
    │   ├── operational states
    │   └── risks
    ├── Orbyn
    │   ├── Orbyn Forge
    │   ├── Orbyn Readiness
    │   ├── Orbyn Guard
    │   ├── Orbyn Data
    │   ├── Orbyn Atlas
    │   │   └── Orbyn Isthmus
    │   ├── Orbyn Adaptive Agent Architecture
    │   ├── Orbyn Synchronicity
    │   └── Orbyn Convergence
    ├── Aegis AI Assurance Guardian
    │   ├── Readiness
    │   ├── Deployment Clearance
    │   ├── Guardrails
    │   ├── Evidence
    │   ├── Incident Readiness
    │   ├── ARIA
    │   ├── Atlas Assurance
    │   └── Tracking Assurance
    ├── DataForge
    ├── Vigilance
    ├── Sovereign Vault
    └── Nexus / Proof Receipts
```

## Functional flow

```text
Business need
→ Readiness / Intake
→ Atlas Case or AI Use Case
→ OAAA Agent Blueprint proposal
→ Aegis risk classification
→ Guardrails plan
→ ARIA adversarial testing
→ Human approval
→ Vigilance permissions
→ Controlled deployment
→ Evidence + Proof Receipt
→ DataForge memory
→ Review and learning
```

## Core entities

| Entity | Purpose |
|---|---|
| Case | Unit of work for Atlas or Aegis |
| Source | Origin, date, confidence, sensitivity |
| Signal | Operational observation linked to a source |
| Risk | Probability, impact, severity, mitigation |
| Scenario | Base, adverse, optimistic, and stress case |
| Stakeholder | Actor affected, influence, exposure |
| Briefing | Executive synthesis and recommended next steps |
| AI Use Case | Tool, data, users, actions, autonomy, owner |
| Agent Blueprint | Proposed agent role, tools, permissions, limits, tests |
| Clearance | Decision, score, conditions, approver, date |
| ARIA Test | Adversarial test, result, severity, remediation |
| Guardrail | Technical or operational control |
| Proof Receipt | Versioned evidence of test and decision |
| Output | Briefing, report, playbook, proposal, or evidence artifact |

## Responsibility boundaries

- **Kernel** governs and records.
- **Orbyn Atlas** generates intelligence.
- **OAAA** proposes and assembles agent blueprints.
- **Aegis** authorizes or blocks deployment.
- **ARIA** challenges behavior.
- **Vigilance** enforces permissions, identities, logs, and approvals.
- **DataForge** stores structured memory and reusable artifacts.
- **Sovereign Vault** protects sensitive material.
- **Nexus** supports continuous evidence and Proof Receipts.

## Architectural rule

No single component may both propose an agent and authorize its production deployment. Separation of duties is mandatory.

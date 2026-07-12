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
    │   ├── Orbyn Signal Depth
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
Document, idea, dilemma or business need
→ Orbyn Signal Depth / Readiness / Intake
→ Decision Card, Atlas Case or AI Use Case
→ Orbyn Forge plan or OAAA Agent Blueprint proposal
→ Aegis risk classification
→ Guardrails plan
→ ARIA adversarial testing
→ Human approval
→ Vigilance permissions
→ Controlled deployment
→ Evidence + Proof Receipt
→ DataForge decision memory
→ Review and learning
```

Orbyn Signal Depth is an entry layer, not an approval or execution layer. It structures documents and decisions, then hands governed objects to the appropriate module.

## Core entities

| Entity | Purpose |
|---|---|
| Case | Unit of work for Atlas or Aegis |
| Signal Depth Input | Original document, idea, note, report or dilemma |
| Depth Run | Versioned processing event with mode, depth, cost and protocol |
| Decision Card | Structured facts, assumptions, risks, options, recommendation, reversible action and change-of-mind threshold |
| Decision Review | Outcome review linked to a committed Decision Card |
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
| Output | Briefing, report, Decision Card, playbook, proposal, or evidence artifact |

## Responsibility boundaries

- **Kernel** governs and records organizations, actors, cases, ownership, sensitivity and state.
- **Orbyn Signal Depth** turns documents, ideas and dilemmas into structured, reviewable decisions.
- **Orbyn Atlas** generates traceable intelligence from sources, signals, risks and scenarios.
- **Orbyn Forge** turns validated decisions into processes, workflows and implementation packages.
- **OAAA** proposes and assembles agent blueprints.
- **Aegis** evaluates risk and authorizes or blocks governed deployment.
- **ARIA** challenges behavior.
- **Vigilance** enforces permissions, identities, logs, approvals and emergency disable.
- **DataForge** stores structured memory, protocols, decision reviews and reusable artifacts.
- **Output Vault** versions outputs and approval states.
- **Sovereign Vault** protects sensitive material and internal doctrine.
- **Nexus** supports continuous evidence, integrity and Proof Receipts.

## Signal Depth architectural decision

Orbyn Signal Depth uses the common Astrynn control plane. It must not create an independent identity, governed database or source of truth.

Target boundary:

```text
Next.js public/private experience
→ common FastAPI/Python domain API
→ Kernel + Signal Depth + Atlas + OAAA + Aegis
→ PostgreSQL/SQLAlchemy + DataForge + Output Vault + Nexus
```

The internal Signal Depth v1000 documents remain confidential and are not stored in this public repository. Public architectural detail is defined in:

- `docs/adr/ADR-001-orbyn-signal-depth-integration.md`;
- `docs/ORBYN_SIGNAL_DEPTH_ROADMAP.md`.

## Architectural rules

- No single component may both propose an agent and authorize its production deployment.
- A generated recommendation is not a human decision or an Aegis authorization.
- A depth level is not a risk classification.
- Signal Depth may route work to Atlas, Forge, OAAA or Aegis, but may not silently execute those modules.
- Separation of duties is mandatory.

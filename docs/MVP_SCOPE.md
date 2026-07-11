# MVP Scope · Phase 1

## Objective

Deliver a usable local MVP that registers an Atlas case or AI use case, produces structured analysis, issues an Aegis decision, records human approval, and generates a Proof Receipt.

## MVP modules

### 1. Kernel Minimum

- users and owners;
- organizations and projects;
- cases and statuses;
- agents and skills;
- decisions and approvals;
- outputs and versions;
- evidence references.

### 2. Orbyn Atlas Case

Inputs:

- title and operational problem;
- sector, country, asset, and horizon;
- sources and confidence;
- stakeholders and sensitivity.

Outputs:

- signals;
- risks;
- four scenarios;
- stakeholder map;
- executive briefing.

### 3. Aegis Deployment Clearance

Assessment dimensions, each scored 0 to 5:

- data;
- permissions;
- autonomy;
- impact;
- traceability;
- human oversight;
- external dependency;
- adversarial robustness;
- incident readiness.

Decision bands:

- 0–10: APTO;
- 11–22: APTO CON CONTROLES;
- 23–34: NO APTO TODAVÍA or strong-controls review;
- 35–45: NO APTO TODAVÍA;
- specialized domains may trigger REQUIERE REVISIÓN ESPECIALIZADA regardless of score.

### 4. ARIA Basic

Initial test families:

- prompt injection;
- data boundary pressure;
- roleplay resistance;
- tool permission drift;
- output safety;
- consistency under pressure;
- incident trigger and escalation.

The MVP records test plans and results. Fully automated offensive testing comes later.

### 5. OAAA Agent Blueprint

The system may propose an agent blueprint containing:

- business need;
- role and objective;
- allowed tools;
- allowed and prohibited data;
- allowed actions;
- autonomy level;
- human approval points;
- required logs;
- test plan;
- rollback and disable procedure.

The blueprint remains `DRAFT` until Aegis and a named human approve it.

### 6. Output Vault and Proof Receipt

Every final output must include:

- case ID;
- artifact type;
- version;
- owner;
- timestamp;
- source references;
- decision;
- conditions;
- approval state;
- optional integrity hash.

## Initial routes

```text
/
/atlas
/atlas/cases
/atlas/case/new
/atlas/case/{id}
/atlas/briefing/{id}
/aegis
/aegis/clearance/new
/aegis/cases
/aegis/case/{id}
/aegis/aria/{id}
/aegis/report/{id}
/oaaa
/oaaa/blueprint/new
/oaaa/blueprint/{id}
/outputs
/kernel
/vigilance
```

## Out of scope

- real-time critical infrastructure feeds;
- automatic external actions;
- self-replication or self-deployment;
- legal certification;
- enterprise SOC implementation;
- production multi-tenancy before security review.

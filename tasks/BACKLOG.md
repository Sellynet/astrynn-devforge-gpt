# Backlog Ejecutivo · Astrynn Meta-OS, Orbyn, Aegis y OAAA

Última actualización: 2026-07-13

Este backlog convierte `docs/BUILD_STATUS.md` en trabajo ejecutable. El documento maestro contiene el alcance completo. Este archivo contiene únicamente bloques priorizados, criterios de salida y dependencias.

## Reglas

- Una tarea marcada como completada significa código fusionado y CI verde, no producción.
- Un módulo no entra en piloto sin persistencia, auth, aislamiento, evidencia, rollback y revisión de seguridad.
- Una rama por bloque y una Pull Request por entrega.
- No se introducen datos reales de clientes en el repositorio público.
- No se construyen Convergence, Critical Assurance ni integraciones críticas antes de cumplir sus gates.
- Synchronicity permanece bloqueado hasta decisión doctrinal.

# COMPLETADO COMO PROTOTIPO

## P0 · Fundación y doctrina

- [x] doctrina integrada Atlas + Aegis + OAAA;
- [x] límites no negociables;
- [x] arquitectura y entidades;
- [x] seguridad y approval gates;
- [x] ADR inicial de stack.

Evidencia: PR #9.

## P1 · Kernel mínimo

- [x] organizaciones, actores, casos, estados y owners;
- [x] eventos y transiciones;
- [x] aprobaciones;
- [x] evidencias y outputs;
- [x] pruebas de lifecycle.

Evidencia: PR #10.

## P2 · Aegis Clearance domain

- [x] AI Use Case;
- [x] nueve dimensiones;
- [x] decisiones;
- [x] specialist triggers;
- [x] hard stops;
- [x] guardrails iniciales;
- [x] Clearance Proof Receipt.

Evidencia: PR #11.

## P3 · Orbyn Atlas domain

- [x] sources;
- [x] signals;
- [x] risks;
- [x] stakeholders;
- [x] cuatro escenarios;
- [x] briefing con facts, inferences, assumptions y recommendations;
- [x] Atlas Proof Receipt.

Evidencia: PR #12.

## P4 · Output Vault domain

- [x] outputs versionados;
- [x] estados;
- [x] evidence references;
- [x] Proof Receipts;
- [x] integrity hash inicial.

Evidencia: PR #13.

## P5 · OAAA Agent Blueprint domain

- [x] blueprint completo;
- [x] lifecycle;
- [x] fingerprints;
- [x] autonomy levels;
- [x] tools, datos, acciones, gates, logs, ARIA, rollback y disable;
- [x] prohibiciones de autoaprobación, autoelevación y autodespliegue.

Evidencia: PR #14.

## P6 · ARIA Test Register domain

- [x] campaigns;
- [x] runs;
- [x] findings;
- [x] severity;
- [x] resolutions;
- [x] ARIA Receipt.

Evidencia: PR #16.

## P7 · Vigilance Permissions domain

- [x] grants;
- [x] action requests;
- [x] approval gates;
- [x] emergency disable state;
- [x] audit records.

Evidencia: PR #17.

## P8 · Private API

- [x] FastAPI;
- [x] OpenAPI;
- [x] Kernel endpoints;
- [x] tests HTTP.

Evidencia: PR #20.

## P9 · Auth y RBAC de desarrollo

- [x] Bearer auth;
- [x] roles;
- [x] organización;
- [x] separación owner/reviewer;
- [x] protección contra actor spoofing.

Evidencia: PR #22.

## P10 · Persistencia Kernel

- [x] repository contract;
- [x] SQLAlchemy;
- [x] SQLite;
- [x] PostgreSQL/Supabase compatibility;
- [x] restart recovery.

Evidencia: PR #24.

## P11 · Aegis Clearance API

- [x] evaluate;
- [x] record;
- [x] permissions;
- [x] organization isolation;
- [x] Output Vault y Evidence linkage.

Evidencia: PR #27.

## P12 · Orbyn Atlas Briefing API

- [x] build;
- [x] record;
- [x] stable IDs;
- [x] source and reference validation;
- [x] permissions;
- [x] persistence linkage.

Evidencia: PR #29.

## P13 · OAAA Blueprint Design API

- [x] create DRAFT;
- [x] read latest and history;
- [x] revise;
- [x] submit to IN_REVIEW;
- [x] fingerprint invalidation;
- [x] RBAC and tenant isolation.

Evidencia: PR #31.

# PRIORIDAD INMEDIATA

## P14 · ARIA API v0.7

- [ ] endpoints de campaigns, runs, findings, resolutions y receipts;
- [ ] permisos ARIA_PLAN, ARIA_EXECUTE, ARIA_REVIEW y ARIA_READ;
- [ ] organization isolation;
- [ ] vínculo obligatorio a case, blueprint y fingerprint;
- [ ] critical finding blocks;
- [ ] tests HTTP;
- [ ] documentación.

Exit criteria:

- ARIA puede registrar una campaña completa sin ejecutar ataques reales;
- findings críticos permanecen abiertos hasta resolución verificada;
- ningún resultado se vincula a un blueprint con fingerprint distinto.

## P15 · Vigilance API v0.8

- [ ] grant requests;
- [ ] approve, deny, revoke and expire;
- [ ] action requests;
- [ ] emergency disable;
- [ ] least privilege validation;
- [ ] tool and operation allowlists;
- [ ] immutable audit trail;
- [ ] tests de escalada de privilegios.

Exit criteria:

- ningún agente puede concederse permisos;
- owner, approver y actor quedan registrados;
- permisos sensibles expiran y pueden revocarse.

## P16 · Persistencia completa del control plane

- [ ] OAAA SQL repository;
- [ ] ARIA SQL repository;
- [ ] Vigilance SQL repository;
- [ ] Output Vault SQL repository;
- [ ] Atlas entity persistence;
- [ ] Aegis Use Case and Clearance persistence;
- [ ] migrations;
- [ ] constraints;
- [ ] restart tests;
- [ ] backup and restore tests.

Exit criteria:

- ningún módulo crítico depende de memoria;
- todas las versiones sobreviven al reinicio;
- historial append-only verificado.

## P17 · Output Vault y Evidence API

- [ ] list, read, approve, reject and supersede outputs;
- [ ] evidence graph;
- [ ] Proof Receipt verification;
- [ ] object storage adapter;
- [ ] download audit;
- [ ] export JSON and Markdown;
- [ ] PDF/DOCX en bloque posterior;
- [ ] permissions and tenant isolation.

Exit criteria:

- cada decisión puede reconstruirse desde su evidencia;
- no existe sobrescritura destructiva;
- integridad verificable.

## P18 · Gates integrados OAAA

- [ ] OAAA → Aegis Clearance;
- [ ] Aegis result bound to blueprint fingerprint;
- [ ] OAAA → ARIA;
- [ ] human approval;
- [ ] Vigilance grants;
- [ ] lifecycle `CLEARED`, `APPROVED`, `BLOCKED`, `SUSPENDED`, `RETIRED`;
- [ ] material changes invalidate prior gates;
- [ ] activation receipt.

Exit criteria:

- no hay autoaprobación;
- no hay saltos manuales invisibles;
- un cambio de tool, data, action o autonomy obliga a re-clearance.

# HARDENING DE PRODUCCIÓN

## P19 · Identidad de producción y tenancy

- [ ] OIDC/OAuth 2.1;
- [ ] MFA;
- [ ] sessions and revocation;
- [ ] service accounts;
- [ ] roles configurable;
- [ ] RLS;
- [ ] tenant leakage tests;
- [ ] audit logs.

## P20 · Seguridad, secrets y supply chain

- [ ] private repository;
- [ ] secret manager;
- [ ] SAST, DAST and dependency scanning;
- [ ] SBOM;
- [ ] signed releases;
- [ ] threat models;
- [ ] OWASP review;
- [ ] pentest before external pilot;
- [ ] security runbooks.

## P21 · Observabilidad y resiliencia

- [ ] structured logs;
- [ ] metrics;
- [ ] traces;
- [ ] alerts;
- [ ] SLOs;
- [ ] backup and restore;
- [ ] disaster recovery;
- [ ] capacity and cost dashboards;
- [ ] incident management.

# EXPERIENCIA DE PRODUCTO

## P22 · Frontend móvil mínimo

- [ ] Next.js/TypeScript shell;
- [ ] login;
- [ ] cases dashboard;
- [ ] approval queue;
- [ ] Aegis form;
- [ ] Atlas builder;
- [ ] OAAA Studio;
- [ ] ARIA panel;
- [ ] Vigilance panel;
- [ ] Output Vault;
- [ ] Proof Receipt view;
- [ ] mobile-safe confirmations;
- [ ] Spanish and English;
- [ ] accessibility.

Exit criteria:

- el CEO puede revisar y aprobar desde móvil;
- ninguna acción sensible ocurre con un toque accidental;
- el flujo principal puede completarse sin portátil.

## P23 · Sandbox y runtime controlado

- [ ] model registry and router;
- [ ] prompt registry;
- [ ] skill registry;
- [ ] tool registry;
- [ ] simulated tools;
- [ ] synthetic data;
- [ ] workers and queues;
- [ ] budgets and rate limits;
- [ ] runtime logging;
- [ ] rollback;
- [ ] kill switch;
- [ ] no self-deployment tests.

Exit criteria:

- solo sandbox;
- ninguna credencial emitida por agente;
- ninguna tool real sin approval y allowlist;
- costes y acciones limitados.

# VALIDACIÓN

## P24 · Alpha interna Astrynn

- [ ] seleccionar caso de bajo riesgo;
- [ ] Need Discovery;
- [ ] OAAA Blueprint;
- [ ] Aegis Clearance;
- [ ] ARIA;
- [ ] human approval;
- [ ] Vigilance;
- [ ] sandbox;
- [ ] output and evidence;
- [ ] incident simulation;
- [ ] rollback;
- [ ] measure time, cost, quality and utility;
- [ ] postmortem.

## P25 · Primer piloto externo

Gates:

- [ ] private repo;
- [ ] production identity;
- [ ] RLS;
- [ ] complete persistence;
- [ ] backups;
- [ ] observability;
- [ ] frontend;
- [ ] legal documents;
- [ ] security review;
- [ ] incident playbook;
- [ ] support.

Ejecución:

- [ ] low-risk client;
- [ ] limited data;
- [ ] sandbox;
- [ ] metrics;
- [ ] stop criteria;
- [ ] evidence pack;
- [ ] continue, redesign or stop decision.

# EXPANSIÓN ORBYN Y AEGIS

## P26 · Aegis product family

- [ ] AI Risk Snapshot;
- [ ] AI Readiness;
- [ ] Guardrails Kit;
- [ ] Evidence Chain;
- [ ] Incident Readiness;
- [ ] Governance Retainer;
- [ ] Training;
- [ ] Tracking Assurance portal;
- [ ] Atlas Assurance;
- [ ] Critical Assurance remains blocked.

## P27 · Orbyn product family

- [ ] Orbyn Readiness;
- [ ] Orbyn Forge;
- [ ] Orbyn Guard;
- [ ] Orbyn Data;
- [ ] Adaptive AgentOps;
- [ ] sector Atlas packs;
- [ ] Synchronicity doctrinal decision;
- [ ] Convergence remains future.

## P28 · Orbyn Isthmus

- [ ] select non-critical Panama use case;
- [ ] public and authorized sources;
- [ ] local stakeholders;
- [ ] Atlas Briefing;
- [ ] Atlas Assurance;
- [ ] institutional demo;
- [ ] pilot agreement;
- [ ] impact metrics;
- [ ] explicit no-control disclaimer.

# COMERCIAL, LEGAL Y OPERACIÓN

## P29 · Packaging y GTM

- [ ] ICP per product;
- [ ] scope and exclusions;
- [ ] pricing;
- [ ] delivery time;
- [ ] support;
- [ ] SLA;
- [ ] onboarding;
- [ ] billing;
- [ ] renewal;
- [ ] demos;
- [ ] sample reports;
- [ ] Ciudad del Saber and Innovar pack.

## P30 · Legal y privacidad

- [ ] privacy notice;
- [ ] terms;
- [ ] DPA;
- [ ] subprocessors;
- [ ] retention;
- [ ] acceptable use;
- [ ] security policy;
- [ ] incident notification;
- [ ] IP and confidentiality;
- [ ] pilot SOW;
- [ ] liability review;
- [ ] DPIA when required;
- [ ] no-certification language.

# BLOQUEOS EXPLÍCITOS

- [ ] No construir Synchronicity hasta decisión doctrinal.
- [ ] No construir Convergence antes de pilotos Atlas/Aegis/OAAA.
- [ ] No construir Critical Assurance sin especialistas y auditoría externa.
- [ ] No conectar infraestructura crítica.
- [ ] No usar datos reales en repositorio público.
- [ ] No permitir self-replication, self-deployment, self-approval ni privilege escalation.

## Regla final

El siguiente bloque técnico es **P14 · ARIA API v0.7**. El roadmap completo y la justificación de cada rama están en `docs/BUILD_STATUS.md`.
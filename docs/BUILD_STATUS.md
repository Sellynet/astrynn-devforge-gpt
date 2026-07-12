# Estado Maestro de Construcción y Roadmap Total

## Astrynn Meta-OS · Orbyn · Aegis AI Assurance Guardian · OAAA

Última actualización: 2026-07-13

## 1. Autoridad y propósito

Este documento es la fuente de verdad operativa para la construcción. Debe responder sin ambigüedad:

1. qué está definido estratégicamente;
2. qué existe realmente como software;
3. qué existe solo como prototipo o pieza parcial;
4. qué queda por construir en toda la familia Orbyn;
5. qué queda por construir en toda la familia Aegis;
6. qué queda por construir en Orbyn Adaptive Agent Architecture;
7. qué capas transversales, controles, pilotos y elementos comerciales siguen pendientes;
8. en qué orden debe ejecutarse el trabajo.

Este documento no sustituye al Documento Maestro Integrado v3.1, al Documento Maestro Aegis v5.0 ni al Vademécum OAAA. Esos documentos gobiernan doctrina, posicionamiento y arquitectura. Este archivo traduce esa doctrina a estado de construcción, dependencias, gates y trabajo pendiente.

Regla de interpretación:

- una especificación no es software;
- un modelo de dominio no es un producto;
- una API privada no es un despliegue comercial;
- un estado `ACTIVE` en OAAA no significa que exista un agente ejecutándose;
- un permiso `ALLOWED` en Vigilance no significa que una acción haya sido ejecutada;
- un Proof Receipt no es una certificación oficial;
- una prueba automatizada verde no demuestra seguridad de producción;
- una narrativa institucional no equivale a un piloto validado.

## 2. Leyenda de estados

| Estado | Significado exacto |
|---|---|
| `COMPLETADO · PROTOTIPO` | Código fusionado, documentado y probado. No implica producto comercial ni producción. |
| `PARCIAL AVANZADO` | Existe núcleo funcional y API, pero faltan persistencia total, UX, integración o controles de producción. |
| `PARCIAL` | Existe una parte útil, pero el módulo no puede operar de extremo a extremo. |
| `NO INICIADO` | Existe definición estratégica, pero no software operativo. |
| `POR DEFINIR` | El nombre o visión existe, pero su alcance doctrinal necesita decisión formal. |
| `FUTURO` | Fuera del MVP y de los primeros pilotos. |
| `BLOQUEADO` | Prohibido avanzar hasta cumplir gates técnicos, legales, financieros o de seguridad. |

## 3. Doctrina invariable

- **Astrynn Holdings** gobierna visión, capital, propiedad intelectual y prioridades.
- **Astrynn Meta-OS** es la arquitectura global que conecta gobierno, agentes, datos, evidencia y operación.
- **Kernel Astrynn** registra organizaciones, actores, casos, estados, owners, decisiones, aprobaciones, riesgos, outputs y evidencias.
- **Orbyn** es la familia comercial y operativa que transforma la arquitectura en productos y Command Centers.
- **Orbyn Atlas** genera inteligencia operativa trazable para empresas, activos, territorios e infraestructuras estratégicas.
- **Aegis AI Assurance Guardian** evalúa, limita, prueba, autoriza o bloquea despliegues de IA, agentes y automatizaciones.
- **OAAA** diseña y ensambla blueprints de agentes adaptados a cada organización bajo gates obligatorios.
- **ARIA** somete casos y blueprints a pruebas adversariales.
- **Vigilance** define y aplica permisos, límites, aprobación humana, observabilidad y capacidad de parada.
- **DataForge** conserva fuentes, datasets, memoria estructurada, versiones, patrones y evidencias reutilizables.
- **Output Vault** conserva outputs versionados y estados de aprobación.
- **Nexus** unifica Proof Receipts, integridad de señal, evidencias y timelines de decisión.
- **Sovereign Vault** custodia material confidencial, credenciales, doctrina roja y propiedad intelectual sensible.
- Ninguna pieza puede proponer, aprobar, conceder permisos y desplegar el mismo agente sin separación de funciones.
- Ningún agente puede autoaprobarse, autoelevar permisos, emitir sus propias credenciales ni autodesplegarse.
- Ningún componente del MVP puede controlar infraestructura crítica real.
- Toda decisión de impacto requiere owner humano, evidencia, rollback, kill switch y revisión.

## 4. Verdad ejecutiva del estado actual

### 4.1 Lo que sí existe

Existe un núcleo Python probado con:

- Kernel gobernado de casos, estados, eventos, owners, aprobaciones, evidencias y outputs;
- Aegis Deployment Clearance determinista;
- nueve dimensiones de riesgo, hard stops, condiciones y guardrails iniciales;
- Orbyn Atlas Case + Briefing con fuentes, señales, riesgos, stakeholders y cuatro escenarios;
- Output Vault y Proof Receipts en el modelo de dominio;
- OAAA Agent Blueprint con lifecycle, fingerprints y prohibiciones;
- ARIA Test Register como dominio;
- Vigilance Permissions Layer como dominio;
- API privada FastAPI;
- autenticación Bearer de desarrollo y RBAC organizativo;
- persistencia Kernel mediante memoria, SQLite o PostgreSQL/Supabase con SQLAlchemy;
- API de Aegis Clearance;
- API de Orbyn Atlas Briefing;
- API de diseño OAAA hasta `IN_REVIEW`;
- pruebas automatizadas con Ruff y pytest.

### 4.2 Lo que todavía no existe

Todavía no existe:

- un producto completo accesible desde móvil;
- identidad de producción con OIDC, SSO y MFA;
- multi-tenancy endurecido con Row Level Security;
- persistencia completa de OAAA, ARIA, Vigilance, Atlas y Output Vault;
- flujo integrado desde necesidad empresarial hasta sandbox y despliegue controlado;
- runtime de agentes;
- conexiones reales con correo, CRM, Drive, Calendar, Slack, Notion, ERPs o APIs externas;
- ejecución segura de tools;
- monitorización runtime completa;
- Aegis Incident Readiness operativo;
- Aegis Evidence Chain completa;
- ARIA runner automatizado;
- Orbyn Forge, Readiness, Guard, Data, Synchronicity o Convergence como productos completos;
- Orbyn Isthmus validado con un piloto real;
- integración con sistemas de infraestructura crítica;
- certificación oficial ni garantía regulatoria.

### 4.3 Evidencia de trabajo fusionado

| Bloque | Estado | Evidencia |
|---|---|---|
| Fundación, doctrina y límites | COMPLETADO · PROTOTIPO | PR #9 |
| Kernel mínimo | COMPLETADO · PROTOTIPO | PR #10 |
| Aegis Clearance domain | COMPLETADO · PROTOTIPO | PR #11 |
| Orbyn Atlas domain | COMPLETADO · PROTOTIPO | PR #12 |
| Output Vault + Proof Receipt domain | COMPLETADO · PROTOTIPO | PR #13 |
| OAAA Agent Blueprint domain | COMPLETADO · PROTOTIPO | PR #14 |
| ARIA Test Register domain | COMPLETADO · PROTOTIPO | PR #16 |
| Vigilance Permissions Layer domain | COMPLETADO · PROTOTIPO | PR #17 |
| API privada y OpenAPI | COMPLETADO · PROTOTIPO | PR #20 |
| Bearer Auth + RBAC | COMPLETADO · PROTOTIPO | PR #22 |
| SQLAlchemy + SQLite/PostgreSQL/Supabase para Kernel | COMPLETADO · PROTOTIPO | PR #24 |
| Aegis Clearance API | COMPLETADO · PROTOTIPO | PR #27 |
| Orbyn Atlas Briefing API | COMPLETADO · PROTOTIPO | PR #29 |
| OAAA Blueprint Design API | COMPLETADO · PROTOTIPO | PR #31 |

## 5. Flujo funcional actual

```text
Identidad Bearer de desarrollo
→ organización y rol
→ Kernel Case
→ Aegis Clearance o Atlas Briefing u OAAA Blueprint DRAFT
→ validaciones deterministas
→ output y evidencia
→ Proof Receipt
→ revisión humana parcial
```

El flujo actual no continúa de forma integrada hacia ARIA, Vigilance, aprobación final, credenciales, sandbox, runtime o despliegue.

# PARTE I · PLATAFORMA COMÚN PENDIENTE

## 6. Repositorios, propiedad intelectual y entornos

Estado: `PARCIAL`.

Pendiente:

- migrar desarrollo operativo y material sensible a repositorio privado;
- mantener el repositorio público solo con código sanitizado, ejemplos sintéticos y documentación segura;
- decidir monorepo o separación entre dominio, API, frontend, infraestructura y documentación confidencial;
- definir CODEOWNERS y ramas protegidas;
- exigir revisión y CI antes de merge;
- separar local, test, staging, pilot y production;
- impedir uso de datos productivos en desarrollo;
- secret scanning, SAST, DAST, dependency scanning, SBOM y control de licencias;
- firma de releases y artefactos;
- changelog, versionado semántico y rollback;
- inventario formal de propiedad intelectual de Astrynn;
- política sobre prompts, datasets, templates y blueprints propietarios.

## 7. Identidad, usuarios y tenancy

Estado: `PARCIAL`.

Construido:

- Bearer tokens de desarrollo;
- roles básicos;
- aislamiento lógico por organización;
- separación owner/reviewer en operaciones críticas.

Pendiente:

- IdP de producción mediante OIDC/OAuth 2.1;
- SSO empresarial;
- MFA para administradores, reviewers y casos sensibles;
- invitaciones, altas, bajas, revocación y recuperación;
- sesiones, refresh tokens, expiración y logout global;
- service accounts para integraciones;
- roles configurables por organización;
- equipos, departamentos, proyectos y delegaciones;
- ABAC adicional por sensibilidad, recurso y acción;
- Row Level Security en PostgreSQL/Supabase;
- pruebas de fuga entre tenants;
- audit logs de acceso;
- políticas condicionales por dispositivo, red o país;
- break-glass controlado.

## 8. Persistencia, migraciones y almacenamiento

Estado: `PARCIAL`.

Construido:

- persistencia Kernel mediante SQLAlchemy;
- soporte de SQLite y PostgreSQL/Supabase.

Pendiente:

- persistencia SQL de OAAA;
- persistencia SQL de ARIA;
- persistencia SQL de Vigilance;
- persistencia SQL de Output Vault;
- persistencia de fuentes, señales, riesgos, escenarios y stakeholders Atlas;
- persistencia de AI Use Cases, scorecards, clearances, guardrails y re-clearances Aegis;
- Alembic o sistema equivalente de migraciones;
- constraints e integridad referencial completas;
- índices, paginación, filtros y búsqueda;
- optimistic locking;
- idempotency keys;
- archivado y retención;
- anonimización y borrado;
- legal hold;
- cifrado de columnas sensibles;
- object storage privado;
- escaneo antivirus y validación de archivos;
- backup cifrado;
- restore probado;
- disaster recovery;
- exportación y portabilidad por organización.

## 9. API, contratos y eventos

Estado: `PARCIAL`.

Pendiente:

- API ARIA;
- API Vigilance;
- API Output Vault y Evidence;
- API Aegis Readiness;
- API Aegis Guardrails;
- API Aegis Incident;
- API completa OAAA más allá de `IN_REVIEW`;
- API Orbyn Forge;
- API Orbyn Readiness;
- API Orbyn Guard;
- API Orbyn Data;
- versionado formal y deprecación;
- paginación, filtros y búsquedas;
- webhooks firmados;
- event bus;
- correlation IDs;
- catálogo de errores estable;
- SDKs;
- rate limiting;
- quotas y budgets;
- retries seguros y circuit breakers;
- protección contra duplicate submissions;
- pruebas de contrato y fuzzing.

## 10. Runtime de IA, modelos, prompts, skills y tools

Estado: `NO INICIADO` como plataforma común.

Pendiente:

- Model Registry;
- Model Router con proveedores permitidos;
- política de selección por coste, riesgo, latencia y sensibilidad;
- Prompt Registry versionado;
- schemas de output;
- Skill Registry;
- Tool Registry;
- allowlists de operaciones por tool;
- adapters para proveedores;
- secrets fuera del agente;
- credenciales de corta duración;
- sandbox de ejecución;
- tools simuladas para pruebas;
- workers y colas para tareas largas;
- scheduler;
- budgets de tokens y coste;
- rate limits por agente y tenant;
- timeouts, retries y circuit breakers;
- evaluación de outputs;
- caché segura;
- redacción de datos sensibles;
- prompt injection controls;
- memoria aislada por tenant y agente;
- trazabilidad de modelo, prompt, contexto y tool call;
- prohibición técnica de self-deployment y self-replication.

## 11. Frontend privado y experiencia móvil

Estado: `NO INICIADO`.

Pendiente crítico:

- frontend Next.js/TypeScript responsive;
- shell común Astrynn/Orbyn/Aegis;
- login y gestión de sesión;
- dashboard ejecutivo;
- dashboard operativo;
- lista y detalle de casos;
- cola de aprobación humana;
- formulario Aegis Clearance;
- constructor Atlas;
- diseñador OAAA;
- panel ARIA;
- panel Vigilance;
- Output Vault y Evidence Explorer;
- visualización de Proof Receipts;
- comentarios y decisiones;
- notificaciones;
- exportaciones;
- modo CEO desde móvil;
- acciones sensibles con confirmación reforzada;
- accesibilidad WCAG;
- español e inglés en primera versión comercial;
- portugués en fase posterior;
- design system Astrynn, Orbyn y Aegis.

## 12. Observabilidad, seguridad y despliegue

Estado: `NO INICIADO` como operación productiva.

Pendiente:

- logs estructurados con redacción de secretos;
- métricas técnicas y de negocio;
- trazas distribuidas;
- alertas;
- SLO, SLA y error budgets;
- runbooks;
- incident management interno;
- health, readiness y liveness checks;
- gestión de vulnerabilidades y parches;
- threat models por módulo;
- OWASP ASVS y API Security review;
- pentest antes de piloto externo;
- secret manager;
- cifrado en tránsito y reposo;
- WAF y DDoS protection;
- contenedores no root;
- infraestructura como código;
- CORS, CSP y CSRF;
- supply-chain protection;
- CI/CD con gates por entorno;
- staging privado;
- rollback de despliegue;
- capacity planning;
- soporte y on-call solo cuando el modelo económico lo justifique.

# PARTE II · TODA LA FAMILIA ORBYN

## 13. Orbyn como capa común

Estado: `PARCIAL` como arquitectura, `NO INICIADO` como producto unificado.

Pendiente:

- Command Center común;
- navegación entre Forge, Readiness, Guard, Data, Atlas y OAAA;
- organización, proyecto, caso, agente y output como objetos compartidos;
- permisos y roles compartidos;
- notificaciones y tareas;
- actividad reciente;
- search global;
- reporting;
- billing y planes en fase comercial;
- administración por cliente;
- plantillas reutilizables;
- métricas de valor, tiempo, riesgo y coste.

## 14. Orbyn Forge

Propósito: Command Centers privados para founders, agencias, consultores y equipos pequeños, capaces de operar ventas, respuestas, documentos, seguimiento y procesos internos.

Estado: `NO INICIADO` como producto. OAAA aporta blueprint, pero Forge todavía no existe como experiencia comercial.

Pendiente:

- Orbyn Forge Pilot;
- intake empresarial;
- mapa AS-IS y TO-BE;
- proceso y workflow canvas;
- detección de tareas deterministas, probabilísticas y humanas;
- catálogo de oportunidades;
- OF-01 SALES;
- OF-02 BLUEPRINT;
- OF-03 BUILD;
- agentes posteriores para respuestas, seguimiento, entrega y aprendizaje;
- Command Center privado;
- bandeja de tareas;
- human approval gates;
- plantillas por ICP;
- integración con OAAA;
- integración con Aegis;
- ARIA plan;
- permisos Vigilance;
- outputs y evidencia;
- estimación de coste y ROI;
- implementación técnica y handoff;
- soporte y AgentOps;
- conectores empresariales solo tras aprobación de seguridad;
- primer piloto pagado;
- validación comercial antes de ampliar plataforma.

Definition of Done de Forge inicial:

- un cliente de bajo riesgo;
- tres procesos delimitados;
- máximo tres agentes;
- datos permitidos documentados;
- Clearance y aprobación humana;
- outputs trazables;
- rollback;
- utilidad y ahorro medidos.

## 15. Orbyn Readiness

Propósito: evaluar madurez organizativa, operativa y técnica para adoptar IA y agentes.

Estado: `NO INICIADO` como producto.

Pendiente:

- cuestionario empresarial;
- inventario de procesos, datos, herramientas, IA, agentes y automatizaciones;
- detección de shadow AI;
- modelo de madurez;
- heatmaps;
- scoring de estrategia, datos, personas, seguridad, gobierno y operaciones;
- owners y accountability;
- sistemas críticos;
- preparación de supervisión humana;
- incident readiness;
- vendor assessment;
- gap analysis;
- plan 30-60-90;
- quick wins y bloqueos;
- Dossier de Evidencias;
- informe ejecutivo y técnico;
- packs sectoriales;
- reevaluación periódica;
- comparación temporal;
- conversión de hallazgos en casos Aegis y blueprints OAAA.

## 16. Orbyn Guard

Propósito: interfaz comercial y operativa de políticas, límites, controles y protección de agentes.

Estado: `NO INICIADO` como producto. Vigilance contiene solo parte del dominio subyacente.

Pendiente:

- catálogo de políticas;
- policy-as-code;
- reglas de datos permitidos y prohibidos;
- límites de contexto y memoria;
- allowlists de modelos, tools y dominios;
- controles pre y post ejecución;
- redacción de datos sensibles;
- output validation;
- prompt injection protection;
- límites de frecuencia, coste y volumen;
- approval gates;
- excepciones temporales;
- kill switch;
- panel de desviaciones;
- control effectiveness testing;
- reporting de cobertura;
- revalidación tras cambios;
- integración con Vigilance, Aegis y OAAA.

## 17. Orbyn Data

Propósito: convertir datos empresariales en una capa gobernada y utilizable por agentes.

Estado: `NO INICIADO` como producto. DataForge existe como visión transversal.

Pendiente:

- catálogo de fuentes y datasets;
- data contracts;
- owners y stewards;
- sensibilidad;
- lineage y provenance;
- quality score;
- frescura;
- deduplicación y reconciliación;
- schemas;
- permisos;
- finalidad y base jurídica cuando corresponda;
- retención y borrado;
- anonimización;
- versionado;
- retrieval seguro;
- índices semánticos aislados;
- leakage tests;
- drift;
- Evidence Pack por dataset;
- conectores aprobados;
- integración con DataForge, Aegis, Atlas y OAAA.

## 18. Orbyn Atlas

Propósito: inteligencia operativa trazable para empresas, activos, territorios e infraestructuras.

Estado: `PARCIAL AVANZADO`. Dominio y API privada construidos.

Pendiente común:

- persistencia SQL de entidades Atlas;
- source registry;
- ingestión manual segura;
- conectores de fuentes públicas;
- provenance y licencias;
- detección de cambios;
- degradación temporal de confianza;
- reconciliación de fuentes contradictorias;
- signal engine;
- taxonomías sectoriales;
- risk register configurable;
- scenario builder avanzado;
- comparación temporal;
- stakeholder graph;
- geospatial layer cuando aporte valor;
- alertas;
- comentarios y decisiones humanas;
- plantillas de briefing;
- exportación PDF, DOCX, Markdown y JSON;
- firma y aprobación;
- Aegis Atlas Assurance;
- ARIA para componentes generativos;
- Output Vault y Nexus;
- dashboard ejecutivo;
- métricas de utilidad y precisión;
- metodología versionada;
- pilotos sintéticos y no críticos.

### 18.1 Orbyn Isthmus

Estado: `NO INICIADO` como piloto real.

Pendiente:

- seleccionar primer problema panameño no crítico;
- mapa de stakeholders;
- taxonomía de logística, agua, puertos, energía, zonas francas y pymes;
- catálogo de datasets públicos y autorizados;
- revisión de licencias;
- fuentes en español e inglés;
- señales, riesgos y escenarios específicos;
- briefings demo;
- revisión de expertos locales;
- propuesta Ciudad del Saber e Innovar;
- pilot agreement;
- métricas de impacto;
- formación y soporte;
- disclaimer de no control del Canal ni infraestructura crítica.

### 18.2 Verticales sectoriales Atlas

| Vertical | Estado | Trabajo pendiente principal |
|---|---|---|
| Orbyn Ports | NO INICIADO | taxonomía portuaria, fuentes, incidentes, tráfico, servicios, partners y piloto no crítico |
| Orbyn Water | NO INICIADO | embalses, sequía, abastecimiento, indicadores, escenarios, expertos hídricos y límites de no control |
| Orbyn Energy | FUTURO CONTROLADO | taxonomía energética, resiliencia, partners técnicos, datos no críticos y revisión especializada |
| Orbyn Airports | FUTURO CONTROLADO | carga, pasajeros, mantenimiento, incidencias, seguridad y piloto estrictamente no operacional |
| Orbyn Cities | FUTURO CONTROLADO | movilidad, servicios, resiliencia, stakeholders públicos, privacidad y piloto delimitado |
| Orbyn Health Infrastructure | BLOQUEADO PARA MVP | especialistas sanitarios, privacidad reforzada, revisión legal, safety case y datos sintéticos antes de cualquier piloto |

Ninguna vertical debe conectarse a sistemas de control reales durante MVP o primeros pilotos.

## 19. Orbyn Adaptive Agent Architecture, OAAA

Propósito: convertir necesidades empresariales en agentes específicos, gobernados y trazables.

Estado: `PARCIAL AVANZADO`. Existe dominio de blueprint y API hasta `IN_REVIEW`. El control plane OAAA sigue en memoria.

Construido:

- necesidad, rol y objetivo;
- tools y operaciones permitidas/prohibidas;
- datos permitidos/prohibidos;
- acciones y autonomía;
- approval points;
- logs;
- plan ARIA;
- rollback y disable;
- versiones;
- safety fingerprint e integrity hash;
- prohibición de wildcards, autoaprobación, autoelevación, credenciales y autodespliegue;
- API de creación, lectura, revisión y envío a revisión.

### 19.1 Need Discovery

Pendiente:

- intake empresarial guiado;
- entrevistas y evidencia;
- process mining ligero;
- clasificación de necesidad;
- impacto, frecuencia, riesgo y ROI;
- decisión de no automatizar cuando corresponda;
- backlog priorizado de candidatos.

### 19.2 Agent Blueprint Studio

Pendiente:

- UI móvil;
- generador asistido;
- alternativas de diseño;
- comparación de agentes;
- catálogo de roles;
- catálogo de skills;
- tool registry;
- data boundary registry;
- schemas de entrada y salida;
- budgets;
- owner y reviewer;
- edición colaborativa;
- comentarios;
- exportación.

### 19.3 Gates integrados

Pendiente crítico:

- persistencia SQL;
- Clearance vinculado al fingerprint exacto;
- ARIA vinculado a la misma versión;
- aprobación humana final;
- Vigilance grants;
- lifecycle API para `CLEARED`, `APPROVED`, `BLOCKED`, `SUSPENDED`, `RETIRED`;
- invalidación automática tras cambio material;
- separación explícita entre activación de gobierno y runtime.

### 19.4 Template y Pattern Library

Pendiente:

- ventas;
- soporte;
- documentación;
- logística;
- análisis;
- compliance pragmático;
- briefing;
- operaciones;
- patrones de human-in-the-loop;
- patrones de escalado y fallo;
- versionado y métricas de reutilización.

### 19.5 Sandbox y Controlled Runtime Builder

Estado: `NO INICIADO`.

Pendiente:

- sandbox aislado;
- tools simuladas;
- datos sintéticos;
- package de prompt, schemas, skills y configuración;
- generación de código solo como propuesta revisable;
- publicación en repositorio privado;
- pipeline separado de despliegue;
- secrets externos;
- rollback runtime;
- kill switch;
- observabilidad;
- cost limits;
- no privilege escalation tests.

### 19.6 Adaptive Agent Factory v1

Estado: `FUTURO CON DEPENDENCIAS`.

La fábrica solo se considera construida cuando puede repetir de forma segura:

```text
Necesidad
→ diagnóstico
→ blueprint
→ Aegis Clearance
→ ARIA
→ aprobación humana
→ permisos Vigilance
→ sandbox
→ evidencia
→ despliegue controlado
→ monitorización
→ re-clearance, suspensión o retirada
```

La organización agéntica podrá proponer y ensamblar nuevos agentes. No podrá autorizarse ni desplegarse a sí misma.

### 19.7 Adaptive AgentOps

Pendiente:

- monitorización mensual;
- drift de prompts, tools, datos y modelos;
- re-clearance;
- nuevas skills;
- cambios de permisos;
- incident linkage;
- performance y coste;
- renovación o retirada;
- reportes al cliente;
- retainer comercial.

## 20. Orbyn Synchronicity

Estado doctrinal: `POR DEFINIR`.

Aclaración obligatoria:

- la última definición explícita en el vademécum fundacional describe Synchronicity como expansión futura hacia vida, hogar, familia y gestión personal;
- el Documento Maestro v3.1 conserva el nombre, pero no redefine formalmente su alcance;
- no debe reinterpretarse silenciosamente como workflow engine o event bus empresarial;
- la coordinación técnica de agentes, eventos, colas y handoffs pertenece por ahora a la plataforma común y al runtime, no automáticamente a Synchronicity.

Decisión pendiente:

1. ratificar Synchronicity como línea futura de vida y hogar;
2. redefinirla formalmente mediante actualización del Documento Maestro;
3. archivarla si deja de aportar valor.

Mientras no exista decisión formal, no se construye producto, API ni branding adicional.

## 21. Orbyn Convergence

Propósito: interfaz futura de visualización avanzada, gemelos digitales, simulación, formación y experiencias inmersivas.

Estado: `FUTURO`.

Pendiente futuro:

- casos de uso con valor comercial real;
- modelos de digital twin no críticos;
- visualización 2D/3D;
- escenarios interactivos;
- formación y simulación;
- integración con Atlas;
- representación de agentes, decisiones y evidencias;
- privacidad;
- rendimiento y streaming;
- AR/VR solo con justificación;
- experiencias B2B/B2G.

No consume recursos del MVP hasta que Atlas, Aegis y OAAA tengan pilotos reales.

# PARTE III · TODA LA FAMILIA AEGIS

## 22. Aegis AI Risk Snapshot

Propósito: entrada comercial de 48-72 horas para identificar exposición visible, shadow AI, datos, permisos y primeras acciones.

Estado: `NO INICIADO` dentro de la plataforma actual.

Pendiente:

- intake corto;
- inventario mínimo;
- checklist de datos y permisos;
- red flags;
- score preliminar;
- top riesgos;
- controles inmediatos;
- decisión de escalar a Readiness o Clearance;
- informe ejecutivo;
- plantilla comercial;
- workflow de venta y entrega;
- evidencia y disclaimer.

## 23. Aegis AI Readiness

Estado: `NO INICIADO` como módulo completo.

Pendiente:

- inventario organizativo;
- casos de uso, agentes, modelos, proveedores y owners;
- madurez de gobierno;
- datos y privacidad;
- seguridad;
- supervisión humana;
- incident readiness;
- vendor risk;
- gaps;
- roadmap 30-60-90;
- Dossier de Evidencias;
- reportes;
- reevaluación;
- integración con Orbyn Readiness;
- conversión de hallazgos en casos Clearance.

## 24. Aegis Deployment Clearance

Estado: `PARCIAL AVANZADO`. Motor y API construidos.

Pendiente:

- persistir AI Use Cases y scorecards;
- Evidence requirement por dimensión;
- historial de re-clearance;
- expiración;
- cambios materiales de modelo, prompt, tool, datos, proveedor o autonomía;
- formularios guiados;
- policy packs por sector;
- hard stops versionados;
- override workflow;
- especialistas externos;
- firma de reviewer;
- condiciones machine-readable;
- comprobación de controles implementados;
- PDF/DOCX;
- comparación de versiones;
- dashboard de aptos, condicionados, bloqueados y caducados;
- integración OAAA;
- métricas de utilidad y error;
- governance de metodología.

## 25. Aegis Guardrails Kit

Estado: `PARCIAL`. Existe biblioteca inicial de recomendaciones.

Pendiente:

- objetos guardrail persistentes;
- owners, estados, evidencias y fechas;
- controles humanos, técnicos y contractuales;
- control library versionada;
- asignación por riesgo y sector;
- exceptions y compensating controls;
- policy-as-code;
- verificación de implementación;
- runtime checks;
- effectiveness testing;
- cobertura;
- revalidación;
- integración con Orbyn Guard y Vigilance.

## 26. Aegis Evidence y Evidence Chain

Estado: `PARCIAL`. Existen outputs, EvidenceReference y Proof Receipts.

Pendiente:

- evidence graph;
- chain of custody;
- object storage;
- clasificación y redacción;
- hashes y firmas;
- evidence bundles;
- Dossier de Evidencias;
- relación requisito-control-test-finding-decisión-aprobación;
- retención, legal hold y expiración;
- permisos;
- watermarking;
- PDF/DOCX/JSON;
- templates por audiencia;
- integrity verification;
- download audit;
- Nexus y Sovereign Vault.

## 27. Aegis Incident Readiness

Estado: `NO INICIADO` como módulo operativo.

Pendiente:

- taxonomía;
- severidad;
- owners y escalado;
- triggers;
- playbooks;
- kill switch;
- contención;
- revocación;
- suspensión;
- preservación de evidencia;
- comunicación;
- timeline;
- postmortem;
- corrective actions;
- re-clearance;
- tabletop exercises;
- MTTA y MTTR;
- integración con Vigilance y soporte.

## 28. ARIA Adversarial Risk & Integrity Audit

Estado: `PARCIAL`. Existe dominio de campañas, runs, findings y receipts.

Pendiente crítico:

- API;
- persistencia SQL;
- test plan builder;
- corpus de pruebas;
- adapters por modelo y proveedor;
- sandbox;
- tool harness;
- prompt injection;
- data boundary pressure;
- role manipulation;
- tool permission drift;
- unsafe output;
- consistency under pressure;
- incident trigger;
- agent-to-agent attacks;
- memory poisoning;
- exfiltration;
- rate y cost abuse;
- regression suites;
- scheduled reruns;
- severity calibration;
- reviewer workflow;
- dashboards;
- red-team manual para alto riesgo;
- vínculo al fingerprint OAAA exacto;
- prohibición de pruebas ofensivas sobre producción sin autorización.

## 29. Aegis Atlas Assurance

Estado: `NO INICIADO` como módulo independiente.

Pendiente:

- licencia y calidad de fuentes;
- trazabilidad source-signal-risk-scenario-briefing;
- facts vs inferences;
- sensibilidad;
- metodología;
- riesgos críticos;
- human review;
- Atlas Assurance Receipt;
- bloqueo de referencias rotas;
- revalidación tras cambios;
- límites territoriales;
- integración con Clearance cuando el briefing alimente acciones o agentes.

## 30. Aegis Tracking Assurance

Estado: `NO INICIADO` dentro de esta plataforma. Existe experiencia histórica de servicio.

Pendiente:

- intake de dominio y stack;
- CMP, GTM, GA4, Meta, Google Ads y CAPI;
- consent states;
- test plan;
- Tag Assistant y Pixel Helper evidence;
- eventos, duplicidades y secuencias;
- Consent Mode v2;
- attribution gap;
- report templates;
- Evidence Pack;
- client portal;
- remediación y retest;
- monitorización periódica;
- integración Aegis Evidence;
- disclaimer de auditoría técnica, no asesoría legal.

## 31. Aegis Training

Estado: `NO INICIADO`.

Pendiente:

- currículum por rol;
- dirección, owners, reviewers, developers y operadores;
- readiness, clearance, guardrails, incidentes y evidencia;
- ejercicios;
- evaluación;
- asistencia;
- renovación;
- español e inglés;
- integración con controles;
- certificados de formación sin presentarlos como certificación regulatoria.

## 32. Aegis Governance Retainer

Estado: `NO INICIADO`.

Pendiente:

- revisión mensual o trimestral;
- nuevos casos;
- re-clearance;
- drift;
- findings ARIA;
- incident trends;
- training;
- control coverage;
- vendor changes;
- executive report;
- SLA y soporte;
- pricing y renovación.

## 33. Aegis Critical Assurance

Estado: `FUTURO Y BLOQUEADO`.

Condiciones previas:

- especialistas sectoriales;
- partners técnicos;
- marco legal y contractual;
- threat model avanzado;
- seguridad demostrada;
- auditoría externa;
- entornos aislados;
- incident response maduro;
- seguro y responsabilidad definidos;
- pruebas independientes.

No se conecta a sistemas críticos durante MVP ni primeros pilotos.

## 34. AI-01 AEGIS

Propósito: primer agente operativo de Aegis para intake, estructuración, exposición, guardrails, coordinación ARIA, incident readiness y propuesta de decisión.

Estado: `PARCIAL`. La lógica determinista de Clearance existe, pero AI-01 como agente completo no existe.

Pendiente:

- intake conversacional controlado;
- carga segura de documentos;
- extracción estructurada;
- preguntas de aclaración;
- detección de campos incompletos;
- clasificación de sensibilidad;
- Exposure Map;
- coordinación con Aegis Clearance;
- preparación de test plan ARIA;
- Incident Mini Playbook;
- generación de informe;
- human handoff;
- Proof Receipt;
- memoria de caso;
- tool permissions;
- límites de autonomía;
- sandbox;
- métricas;
- tests de alucinación, omisión y manipulación;
- prohibición de decisión final autónoma.

# PARTE IV · CAPAS TRANSVERSALES

## 35. Kernel Astrynn

Estado: `PARCIAL`.

Pendiente:

- persistencia completa;
- migraciones;
- organizaciones, equipos y proyectos avanzados;
- Policy Registry;
- Decision Registry;
- Risk Registry global;
- dependency graph;
- budgets;
- estados corporativos;
- domain events;
- API administrativa;
- reporting;
- search;
- tenancy endurecido;
- retención;
- integración total.

## 36. DataForge

Estado: `NO INICIADO` como plataforma.

Pendiente:

- Source Registry;
- Dataset Registry;
- Evidence Registry;
- lineage;
- provenance;
- versionado;
- quality scores;
- Schema Registry;
- data contracts;
- semantic memory;
- retrieval indexes aislados;
- knowledge graph;
- pattern library;
- templates;
- retention y deletion;
- observabilidad de calidad;
- integración Atlas, Aegis, OAAA y Nexus.

## 37. Vigilance

Estado: `PARCIAL`. Existe dominio de permisos.

Pendiente:

- API grants y action requests;
- persistencia;
- panel;
- enforcement adapters;
- secret manager;
- credenciales de corta duración por proveedor autorizado;
- aprobación, revocación y expiración;
- emergency disable operativo;
- audit logs runtime;
- policy violations;
- budgets;
- tool proxy/gateway;
- action receipts;
- alertas;
- incident integration;
- privilege escalation tests.

## 38. Output Vault

Estado: `PARCIAL`.

Pendiente:

- persistencia SQL;
- object storage;
- API;
- aprobación, rechazo y supersesión;
- firmas;
- exportaciones;
- búsqueda;
- permisos;
- retención;
- legal hold;
- download audit;
- UI;
- backup y restore.

## 39. Sovereign Vault

Estado: `NO INICIADO` como servicio técnico.

Pendiente:

- clasificación soberana;
- repositorio privado separado;
- cifrado fuerte;
- key management;
- mínimo privilegio;
- break-glass;
- audit logs;
- backup offline o equivalente;
- control de exportación;
- recuperación;
- documentación roja;
- credenciales fuera del código;
- separación comercial, operativa y estratégica.

## 40. Nexus y Proof Receipts

Estado: `PARCIAL`.

Pendiente:

- Receipt Registry global;
- timeline caso-blueprint-clearance-ARIA-permisos-aprobación-output-incidente;
- integrity verification;
- control coverage;
- expiraciones;
- missing evidence;
- receipt comparison;
- Assurance Pack;
- vistas auditor, cliente y executive;
- Signal Integrity y drift.

## 41. SSTO y Strategy Stack

Estado: `NO INICIADO` como sistema corporativo.

Pendiente:

- portfolio de iniciativas IA;
- ownership;
- presupuesto;
- prioridades;
- policies;
- risk appetite;
- métricas;
- reporting CEO;
- revisiones;
- vendor governance;
- model registry corporativo;
- exceptions;
- training register;
- incident trends;
- integración Kernel/Aegis.

# PARTE V · PRODUCTO, PILOTOS, LEGAL Y NEGOCIO

## 42. Paquetes comerciales pendientes

- Aegis AI Risk Snapshot;
- Aegis Deployment Clearance;
- Aegis Readiness;
- Aegis Guardrails Kit;
- ARIA Adversarial Audit;
- Aegis Governance Retainer;
- Aegis Tracking Assurance;
- Orbyn Blueprint;
- Orbyn Forge Pilot;
- Orbyn Readiness;
- OAAA Agent Blueprint Design;
- OAAA Pilot;
- Controlled Deployment;
- Adaptive AgentOps;
- Atlas Briefing Pilot;
- Atlas + Aegis + OAAA Pilot;
- Orbyn Isthmus institutional pilot.

Para cada paquete falta cerrar:

- ICP;
- problema comprado;
- alcance;
- precio;
- inputs;
- entregables;
- exclusiones;
- duración;
- soporte;
- SLA;
- términos;
- evidencia;
- criterios de éxito;
- renovación.

## 43. Demos y casos de muestra

Pendiente:

- Aegis APTO;
- Aegis APTO CON CONTROLES;
- Aegis NO APTO;
- Aegis revisión especializada;
- Atlas no crítico;
- Isthmus sintético;
- OAAA blueprint completo;
- ARIA campaign;
- Vigilance permissions;
- Incident simulation;
- Proof Receipt pack;
- demo ejecutiva de 10 minutos;
- demo técnica de 30 minutos;
- walkthrough móvil.

## 44. Piloto interno Astrynn

Pendiente:

- seleccionar caso de bajo riesgo;
- usar datos sintéticos, públicos o aprobados;
- Kernel Case;
- OAAA Blueprint;
- Aegis Clearance;
- ARIA;
- human approval;
- Vigilance grants;
- sandbox;
- outputs y evidence;
- incidente y rollback;
- coste, calidad, tiempo y utilidad;
- postmortem.

## 45. Piloto externo

Gates obligatorios:

- repositorio privado;
- identidad de producción;
- RLS;
- persistencia completa;
- secrets;
- backups;
- observabilidad;
- frontend mínimo;
- privacy notice, DPA y SOW;
- security review;
- incident playbook;
- soporte.

Después:

- cliente de bajo riesgo;
- alcance limitado;
- sandbox;
- métricas;
- criterios de parada;
- revisión periódica;
- Evidence Pack final.

## 46. Panamá, Ciudad del Saber e Innovar

Pendiente:

- narrativa institucional actualizada;
- one-page;
- deck;
- dossier técnico;
- dossier de riesgos y límites;
- demo Isthmus;
- stakeholders y partners;
- reuniones exploratorias;
- piloto no crítico;
- presupuesto;
- propiedad intelectual y jurisdicción;
- impacto local y empleo;
- modelo de colaboración;
- Panama AI Operations Lab solo tras demanda real.

## 47. Legal, privacidad y contractual

Pendiente:

- privacy notice;
- terms;
- DPA;
- subprocessors;
- retention policy;
- security policy;
- acceptable use;
- incident notification;
- AI limitations;
- no-certification disclaimer;
- IP ownership;
- confidentiality;
- pilot agreement;
- professional liability review;
- DPIA cuando proceda;
- revisión especializada para sectores regulados.

# PARTE VI · ORDEN DE EJECUCIÓN

## 48. Fase A · Completar control plane

Prioridad inmediata:

1. API ARIA;
2. API Vigilance;
3. persistencia OAAA, ARIA, Vigilance, Atlas y Output Vault;
4. API Output Vault/Evidence;
5. migraciones formales;
6. RLS;
7. IdP y MFA;
8. secrets;
9. backup/restore;
10. observabilidad.

Exit criteria:

- ningún módulo crítico en memoria;
- aislamiento probado;
- recuperación probada;
- logs y alertas;
- seguridad revisada.

## 49. Fase B · Circuito gobernado integrado

```text
Need Discovery
→ OAAA Blueprint
→ Aegis Clearance
→ ARIA
→ Human Approval
→ Vigilance Grants
→ Sandbox
→ Output Vault
→ Proof Receipt
→ Monitoring
→ Re-clearance, suspension o retirement
```

Exit criteria:

- fingerprints compartidos;
- cambios materiales invalidan decisiones anteriores;
- no hay autoaprobación;
- rollback y disable probados;
- evidencia completa.

## 50. Fase C · Frontend móvil y alpha interna

- shell móvil;
- un caso Aegis;
- un caso Atlas;
- un blueprint OAAA;
- ARIA;
- Vigilance;
- sandbox con tools simuladas;
- evidencia;
- incidente;
- medición de coste y utilidad.

## 51. Fase D · Primer piloto externo

- cliente de bajo riesgo;
- datos limitados;
- sin sistemas críticos;
- contrato;
- métricas;
- soporte;
- evidence pack;
- decisión continuar/rediseñar/detener.

## 52. Fase E · Orbyn Isthmus

- problema no crítico en Panamá;
- fuentes públicas y autorizadas;
- Atlas Briefing;
- Atlas Assurance;
- demo institucional;
- partner local;
- piloto controlado.

## 53. Fase F · Expansión Orbyn y Aegis

Orden recomendado después del núcleo:

1. Aegis Readiness y Risk Snapshot;
2. Orbyn Readiness;
3. Orbyn Forge;
4. Orbyn Guard;
5. Orbyn Data;
6. Aegis Incident y Evidence avanzada;
7. Tracking Assurance en portal;
8. Atlas sectorial;
9. AgentOps y Governance Retainer;
10. Synchronicity solo tras decisión doctrinal;
11. Convergence en futuro.

# PARTE VII · DEFINITIONS OF DONE

## 54. Prototype Done

- especificación;
- código;
- tests;
- documentación;
- sin secretos;
- CI verde.

## 55. MVP Done

- flujo usable;
- persistencia;
- auth y RBAC;
- evidence;
- rollback;
- mobile UX mínima;
- errores seguros;
- datos sintéticos o aprobados;
- revisión interna.

## 56. Pilot Ready

- repositorio privado;
- identidad de producción;
- RLS;
- migrations;
- backups;
- observabilidad;
- security review;
- legal/contractual;
- incident playbook;
- soporte;
- no findings críticos abiertos.

## 57. Product Ready

- pilotos exitosos;
- estabilidad;
- métricas;
- customer success;
- billing;
- SLAs;
- auditoría de seguridad;
- mantenimiento;
- documentación y training;
- economía sostenible.

# PARTE VIII · PROHIBICIONES

## 58. No se permite actualmente

- datos reales de clientes en repositorio público;
- secretos en GitHub, issues, documentos o screenshots;
- API pública actual;
- infraestructura crítica;
- self-replication;
- self-deployment;
- autoelevación;
- autoaprobación;
- acciones destructivas sin gate humano;
- desactivar logs;
- borrar evidencia;
- presentar `ACTIVE` como runtime;
- presentar `ALLOWED` como ejecución;
- presentar Proof Receipt como certificación;
- prometer cumplimiento automático;
- presentar escenarios Atlas como predicciones;
- construir Critical Assurance sin especialistas;
- construir Convergence antes del núcleo;
- construir Synchronicity sin decisión doctrinal.

## 59. Próximos bloques ejecutables

1. API ARIA.
2. API Vigilance.
3. persistencia del control plane OAAA/ARIA/Vigilance/Output Vault.
4. Output Vault y Evidence API.
5. gates integrados OAAA → Aegis → ARIA → Human → Vigilance.
6. frontend móvil mínimo.
7. identidad de producción, RLS y migrations.
8. sandbox de agentes con tools simuladas.
9. alpha interna.
10. primer piloto externo de bajo riesgo.

## 60. Conclusión ejecutiva

Astrynn ya dispone de una base doctrinal y tecnológica seria para Kernel, Aegis Clearance, Orbyn Atlas, OAAA, ARIA, Vigilance y evidencia. Esa base es un prototipo gobernado, no todavía una organización agéntica comercial completa.

El objetivo central no es multiplicar nombres ni construir todas las ramas simultáneamente. El objetivo es cerrar primero el circuito:

**necesidad → blueprint → clearance → pruebas → aprobación → permisos → sandbox → evidencia → monitorización → revisión.**

Cuando ese circuito funcione con persistencia, seguridad, móvil, rollback y un piloto de bajo riesgo, se expandirán Orbyn Forge, Readiness, Guard, Data, Atlas sectorial, Aegis Readiness, Incident, Governance Retainer y AgentOps. Synchronicity requiere decisión doctrinal. Convergence permanece en el horizonte futuro.
# Build Status y Roadmap Maestro Completo · Astrynn Meta-OS, Orbyn y Aegis

Última actualización: 2026-07-13

## 1. Propósito de este documento

Este documento es la referencia operativa para responder, sin ambigüedad, a cuatro preguntas:

1. Qué se ha definido estratégicamente.
2. Qué se ha construido realmente como software.
3. Qué todavía no existe o solo existe de forma parcial.
4. Qué queda por construir en todas las ramas de Orbyn, Aegis AI Assurance Guardian, Orbyn Adaptive Agent Architecture y las capas transversales de Astrynn Holdings.

No debe interpretarse una especificación, un modelo de dominio, una prueba automatizada, un estado `ACTIVE` o un Proof Receipt como si fueran un despliegue productivo real. La arquitectura está avanzando de forma controlada, pero todavía no existe un sistema comercial completo, conectado a clientes o autorizado para operar sobre infraestructura crítica.

## 2. Doctrina invariable

- **Orbyn** es la familia operativa y comercial que transforma necesidades empresariales en sistemas de agentes, inteligencia, procesos y Command Centers gobernados.
- **Orbyn Atlas** observa, estructura, analiza y simula señales, riesgos, escenarios y decisiones para activos, organizaciones, territorios e infraestructuras estratégicas.
- **Aegis AI Assurance Guardian** evalúa, limita, prueba, autoriza o bloquea el despliegue de sistemas de IA y agentes, dejando evidencia verificable.
- **Orbyn Adaptive Agent Architecture, OAAA**, diseña y ensambla blueprints de agentes adaptados a una empresa, pero no puede autoautorizar, autoelevar permisos, emitir credenciales ni autodesplegarse.
- **ARIA** somete blueprints y sistemas a pruebas adversariales.
- **Vigilance** registra y aplica permisos, límites, aprobaciones y desactivación de emergencia.
- **DataForge** conserva memoria estructurada, fuentes, versiones, evidencias y conocimiento reutilizable.
- **Sovereign Vault** custodia material sensible y estratégico.
- **Nexus y Output Vault** organizan outputs, decisiones, evidencia y Proof Receipts.
- **Kernel Astrynn** registra organizaciones, actores, casos, estados, owners, aprobaciones, evidencias y decisiones.
- Ninguna pieza puede simultáneamente proponer un agente, aprobarlo, concederle permisos y desplegarlo.
- Ningún componente del MVP puede controlar infraestructura crítica real.
- Toda decisión de impacto mantiene un owner humano identificable, trazabilidad, rollback y capacidad de parada.

## 3. Leyenda de estados

| Estado | Significado exacto |
|---|---|
| `COMPLETADO · PROTOTIPO` | Existe código probado y fusionado, pero no implica producción comercial. |
| `PARCIAL` | Existe una parte funcional, pero faltan integraciones, persistencia, interfaz o controles. |
| `NO INICIADO` | Está definido estratégicamente, pero no existe todavía como módulo operativo. |
| `FUTURO` | No forma parte del MVP ni de los primeros pilotos. |
| `BLOQUEADO` | No debe ejecutarse hasta cumplir gates técnicos, legales o de seguridad. |

## 4. Resumen ejecutivo verdadero

### 4.1 Lo que existe hoy

Existe un núcleo Python probado con:

- Kernel gobernado de casos, estados, owners, eventos, aprobaciones, evidencias y outputs.
- Aegis Deployment Clearance con nueve dimensiones, decisiones, guardrails y Proof Receipt.
- Orbyn Atlas Case + Briefing con fuentes, señales, riesgos, stakeholders, cuatro escenarios y trazabilidad.
- Output Vault y Proof Receipts append-only en su modelo de dominio.
- OAAA Agent Blueprint con lifecycle, fingerprint, restricciones y gates de gobierno.
- ARIA Test Register con campañas, runs, findings, resoluciones y recibos.
- Vigilance Permissions Layer con grants, acciones, approval gates y emergency disable.
- API privada FastAPI.
- autenticación Bearer de desarrollo y RBAC organizativo.
- persistencia Kernel mediante memoria, SQLite o PostgreSQL/Supabase vía SQLAlchemy.
- API de Aegis Clearance.
- API de Orbyn Atlas Briefing.
- API de diseño de blueprints OAAA hasta el estado `IN_REVIEW`.
- pruebas automatizadas con Ruff y pytest.

### 4.2 Lo que todavía no existe

Todavía no existe un producto completo con:

- identidad de producción, SSO, OIDC, MFA y recuperación de cuentas;
- multi-tenancy endurecido con Row Level Security;
- persistencia completa de OAAA, ARIA, Vigilance y Output Vault;
- frontend privado adaptado al móvil;
- flujo integrado extremo a extremo desde necesidad empresarial hasta despliegue controlado;
- ejecución sandbox de agentes;
- conexiones reales con herramientas empresariales;
- despliegue de agentes en producción;
- monitorización runtime completa;
- Aegis Incident Readiness operativo;
- Aegis Evidence como dossier completo y cadena de custodia;
- Orbyn Forge, Readiness, Guard, Data, Synchronicity o Convergence como productos completos;
- Orbyn Isthmus validado mediante un piloto institucional en Panamá;
- integración con datos reales de infraestructuras críticas;
- certificación oficial, garantía legal o cumplimiento regulatorio automático.

## 5. Trabajo completado y evidencia

| Bloque | Estado | Evidencia |
|---|---|---|
| Fundación, doctrina y límites no negociables | COMPLETADO · PROTOTIPO | PR #9 |
| Kernel mínimo gobernado | COMPLETADO · PROTOTIPO | PR #10 |
| Aegis Deployment Clearance | COMPLETADO · PROTOTIPO | PR #11 |
| Orbyn Atlas Case + Briefing | COMPLETADO · PROTOTIPO | PR #12 |
| Output Vault + Proof Receipt | COMPLETADO · PROTOTIPO | PR #13 |
| OAAA Agent Blueprint | COMPLETADO · PROTOTIPO | PR #14 |
| ARIA Test Register | COMPLETADO · PROTOTIPO | PR #16 |
| Vigilance Permissions Layer | COMPLETADO · PROTOTIPO | PR #17 |
| API privada y OpenAPI | COMPLETADO · PROTOTIPO | PR #20 |
| Bearer Auth + RBAC organizativo | COMPLETADO · PROTOTIPO | PR #22 |
| SQLAlchemy + SQLite/PostgreSQL/Supabase para Kernel | COMPLETADO · PROTOTIPO | PR #24 |
| Aegis Clearance API | COMPLETADO · PROTOTIPO | PR #27 |
| Orbyn Atlas Briefing API | COMPLETADO · PROTOTIPO | PR #29 |
| OAAA Agent Blueprint Design API | COMPLETADO · PROTOTIPO | PR #31 |

## 6. Flujo funcional actual

```text
Identidad Bearer de desarrollo
→ organización y rol
→ Kernel Case
→ Aegis Clearance o Atlas Briefing u OAAA Blueprint DRAFT
→ validaciones deterministas
→ output y evidencia
→ Proof Receipt
→ revisión humana
```

El flujo actual no continúa automáticamente hacia ARIA, Vigilance, aprobación final, credenciales, runtime o despliegue.

# PARTE I · TODO LO QUE QUEDA POR HACER EN LA PLATAFORMA COMÚN

## 7. Repositorios, entornos y protección de propiedad intelectual

### Pendiente crítico

- Migrar el desarrollo operativo a un repositorio privado antes de introducir información de clientes, prompts propietarios, playbooks completos, credenciales o material del Sovereign Vault.
- Decidir si se mantiene un monorepo o se separan dominio, API, frontend, infraestructura y documentación confidencial.
- Definir ramas protegidas, CODEOWNERS, revisión obligatoria y firmas de commits.
- Crear entornos separados: local, test, staging, pilot y production.
- Impedir que datos de producción entren en test o desarrollo.
- Incorporar secret scanning, dependency scanning, SAST, DAST, SBOM y control de licencias.
- Establecer política de versiones, changelog, releases y rollback.
- Crear un inventario formal de propiedad intelectual de Astrynn.

## 8. Identidad, usuarios y tenancy

### Construido parcialmente

- Bearer tokens de desarrollo.
- roles básicos y aislamiento lógico por organización.

### Pendiente

- IdP de producción mediante OIDC/OAuth 2.1.
- MFA obligatorio para administradores, reviewers y owners de casos sensibles.
- invitaciones, altas, bajas, recuperación y revocación de cuentas.
- sesiones, expiración, rotación de refresh tokens y logout global.
- service accounts para integraciones no humanas.
- roles configurables por organización.
- equipos, departamentos, proyectos y delegaciones temporales.
- separación entre administrador de plataforma, administrador de organización, owner, reviewer, auditor, operador y viewer.
- Row Level Security en PostgreSQL/Supabase.
- pruebas de fuga entre tenants.
- auditoría de acceso y exportación de logs.
- políticas de acceso condicional por sensibilidad, país, dispositivo o red.

## 9. Persistencia, migraciones y datos

### Construido parcialmente

- Kernel persistente mediante SQLAlchemy.
- soporte técnico para SQLite y PostgreSQL/Supabase.

### Pendiente

- Persistencia SQL de OAAA, ARIA, Vigilance y Output Vault.
- Persistencia de objetos Atlas como entidades de primera clase: fuentes, señales, riesgos, escenarios y stakeholders.
- Persistencia versionada de AI Use Cases, scorecards, guardrails y clearances Aegis.
- Alembic o sistema equivalente de migraciones revisadas.
- restricciones de integridad y claves foráneas completas.
- índices, paginación, filtros y búsquedas.
- idempotency keys para endpoints de escritura.
- optimistic locking y prevención de conflictos de edición.
- cifrado de columnas sensibles.
- políticas de retención, legal hold, borrado y anonimización.
- exportación y portabilidad de datos por organización.
- backup, restore y pruebas periódicas de recuperación.
- métricas de crecimiento y capacidad.
- archivado de casos cerrados.
- object storage privado para archivos de evidencia.
- antivirus y validación de archivos subidos.

## 10. API y contratos

### Pendiente

- API de ARIA.
- API de Vigilance.
- API de Output Vault.
- API de Aegis Readiness, Guardrails, Evidence e Incident.
- API completa de OAAA más allá de `IN_REVIEW`.
- API de Orbyn Forge, Readiness, Guard, Data y Synchronicity.
- versionado formal `/api/v1`, compatibilidad y política de deprecación.
- paginación, orden, filtros y búsqueda.
- webhooks firmados.
- rate limiting por organización, usuario y endpoint.
- límites de coste y consumo.
- circuit breakers y retries seguros.
- manejo de concurrencia y duplicate submissions.
- catálogo de errores estable.
- OpenAPI contractual y generación de SDKs.
- trazabilidad de cada petición con correlation ID.
- pruebas de contrato y fuzzing de inputs.

## 11. Frontend y experiencia móvil

### Pendiente crítico para el usuario

- Frontend privado responsive y optimizado para móvil.
- dashboard de organizaciones, casos y tareas pendientes.
- cola de aprobaciones humanas.
- formularios Aegis Clearance y Readiness.
- constructor Atlas Case y visualización de escenarios.
- diseñador OAAA de blueprints.
- panel ARIA de campañas y findings.
- panel Vigilance de permisos y acciones.
- Output Vault y Evidence Explorer.
- vista de Proof Receipts.
- notificaciones y comentarios.
- exportación de informes.
- modo lectura ejecutiva para CEO.
- accesibilidad WCAG.
- español e inglés desde la primera versión comercial; portugués posteriormente.
- diseño system de Astrynn, Orbyn y Aegis.
- protección frente a acciones accidentales desde móvil.

## 12. Observabilidad y operación

### Pendiente

- logs estructurados con redacción de secretos.
- métricas técnicas y de negocio.
- trazas distribuidas.
- dashboards de latencia, errores, coste, uso y riesgo.
- alertas técnicas y de seguridad.
- health, readiness y liveness checks.
- monitorización de colas y tareas largas.
- incident management interno.
- runbooks de soporte.
- SLO, SLA y error budgets.
- status page privada o pública según fase.
- auditoría de cambios administrativos.
- capacity planning.

## 13. Seguridad técnica y despliegue

### Pendiente crítico

- threat model por módulo.
- revisión OWASP ASVS y API Security Top 10.
- pentest antes de piloto externo.
- gestión de secretos mediante Vault, Doppler, 1Password Secrets Automation o equivalente.
- cifrado en tránsito y en reposo.
- WAF y protección DDoS mediante Cloudflare.
- contenedores endurecidos y ejecución no root.
- infraestructura como código.
- separación de redes y bases.
- políticas CORS y CSP.
- protección CSRF cuando exista frontend con cookies.
- rotación de claves.
- backup cifrado y restore probado.
- disaster recovery.
- gestión de vulnerabilidades y parches.
- protección de supply chain.
- firma de artefactos de despliegue.
- revisión de seguridad para proveedores de modelos y herramientas.

# PARTE II · TODO LO QUE QUEDA POR HACER EN ORBYN

## 14. Orbyn como familia operativa

Orbyn no es un solo agente ni una única aplicación. Es una familia de productos y capacidades que debe convertir necesidades empresariales en sistemas gobernados. Cada rama tiene propósito propio y debe integrarse con Kernel, Aegis, ARIA, Vigilance, DataForge y Output Vault.

## 15. Orbyn Forge

### Propósito

Convertir necesidades, procesos y tareas empresariales en workflows, blueprints y paquetes de implementación gobernados.

### Estado

`NO INICIADO` como producto. OAAA proporciona parte del núcleo de blueprint, pero Forge todavía no existe como experiencia de construcción.

### Pendiente completo

- intake de necesidad empresarial.
- descubrimiento y modelado de procesos.
- mapa AS-IS y TO-BE.
- identificación de tareas humanas, deterministas y probabilísticas.
- catálogo de oportunidades de automatización.
- workflow canvas.
- catálogo de agentes, skills, tools y templates.
- constructor de flujos con approval gates.
- simulación del proceso antes de construir.
- estimación de coste, riesgo, tiempo y retorno.
- generación de blueprint OAAA.
- vinculación automática con Aegis Clearance.
- generación del plan ARIA.
- generación de permisos Vigilance.
- generación del dossier de evidencias.
- versionado y comparación de workflows.
- biblioteca sectorial de patrones.
- paquete de handoff para implementación técnica.
- gestión de cambios y re-clearance.
- catálogo de conectores aprobados.
- métricas del proceso.
- dashboard de valor entregado.
- integración con humanos, tickets y aprobaciones.
- marketplace interno de componentes reutilizables, solo en fase posterior.

## 16. Orbyn Readiness

### Propósito

Evaluar si una empresa está preparada organizativa, operativa y técnicamente para adoptar agentes e inteligencia operativa.

### Estado

`NO INICIADO` como producto. Existen documentos y doctrina, pero no un módulo completo.

### Pendiente completo

- cuestionario de intake empresarial.
- inventario de procesos, datos, herramientas y responsables.
- inventario de IA, agentes y automatizaciones existentes.
- modelo de madurez.
- scoring por estrategia, datos, personas, seguridad, operaciones y gobierno.
- detección de shadow AI.
- mapa de dependencias y riesgos.
- clasificación de sistemas críticos.
- análisis de capacidad de supervisión humana.
- análisis de preparación ante incidentes.
- gap analysis.
- plan 30-60-90 días.
- priorización de quick wins y proyectos bloqueados.
- Dossier de Evidencias de readiness.
- informe ejecutivo y técnico.
- reevaluación periódica.
- comparación entre periodos.
- packs por sector.
- integración con Aegis Readiness y OAAA.
- conversión de hallazgos en backlog accionable.

## 17. Orbyn Guard

### Propósito

Ofrecer la capa visible y operativa de políticas, límites, controles y protección de agentes y workflows.

### Estado

`NO INICIADO` como producto. Vigilance contiene parte de la lógica de permisos, pero Orbyn Guard todavía no existe.

### Pendiente completo

- catálogo de políticas empresariales.
- policy-as-code.
- reglas de datos permitidos y prohibidos.
- límites de contexto y memoria.
- allowlists de modelos, herramientas y dominios.
- controles pre-ejecución y post-ejecución.
- redacción y tokenización de datos sensibles.
- validación de outputs.
- protección frente a prompt injection.
- límites de frecuencia, coste y volumen.
- reglas de aprobación humana.
- excepciones temporales y su evidencia.
- integración con Vigilance.
- kill switch y suspensión.
- monitorización de policy violations.
- panel de incidentes y desviaciones.
- informes de controles activos.
- pruebas de efectividad de guardrails.
- revalidación tras cambios de modelo, tool o prompt.

## 18. Orbyn Data

### Propósito

Convertir datos empresariales en una capa gobernada y utilizable por agentes y sistemas de inteligencia.

### Estado

`NO INICIADO` como producto. DataForge está definido como capa transversal, pero Orbyn Data no tiene todavía producto ni interfaz.

### Pendiente completo

- catálogo de fuentes y datasets.
- data contracts.
- clasificación de sensibilidad.
- owner y steward por dataset.
- lineage y provenance.
- evaluación de calidad.
- reglas de frescura.
- control de duplicados y conflictos.
- esquema y validación.
- permisos de acceso.
- finalidad y base jurídica cuando corresponda.
- retención y borrado.
- anonimización y pseudonimización.
- versionado de datasets.
- preparación de datos para retrieval.
- índices semánticos aislados por tenant.
- evaluación de contaminación y leakage.
- monitorización de drift.
- evidence pack de cada dataset.
- integración con DataForge, Aegis y OAAA.
- conectores solo después de validación de seguridad.

## 19. Orbyn Atlas

### Propósito

Producir inteligencia operativa trazable para activos, empresas, territorios e infraestructuras estratégicas.

### Estado

`PARCIAL`. Existen dominio, briefing determinista y API privada.

### Pendiente completo

- persistir fuentes, señales, riesgos, escenarios y stakeholders como entidades SQL.
- registrar versiones y cambios de cada objeto.
- interfaz de creación y revisión de casos.
- source registry con fecha, confianza, sensibilidad y provenance.
- ingestión manual segura.
- conectores de datos públicos y abiertos.
- conectores internos solo tras clearance.
- detección de cambios en fuentes.
- degradación temporal de confianza.
- reglas de reconciliación de fuentes contradictorias.
- signal engine.
- taxonomías sectoriales.
- risk register completo.
- matrices de probabilidad e impacto configurables.
- scenario builder avanzado.
- comparación temporal de escenarios.
- stakeholder graph.
- mapas geográficos cuando sean necesarios.
- horizonte temporal y calendario de revisión.
- alertas de señales y riesgos.
- comentarios y decisiones humanas.
- plantillas de briefing por sector.
- exportación PDF, DOCX, JSON y Markdown.
- firma y aprobación del briefing.
- Atlas Assurance mediante Aegis.
- integración con ARIA cuando se utilicen modelos generativos.
- integración con Output Vault y Nexus.
- dashboard ejecutivo.
- métricas de utilidad, precisión y adopción.
- metodología documentada y versionada.
- pilot cases sintéticos y no críticos.

## 20. Orbyn Isthmus

### Propósito

Primer despliegue territorial de Orbyn Atlas en Panamá, centrado inicialmente en análisis, escenarios, formación y apoyo a decisiones con datos públicos, abiertos, manuales o no críticos.

### Estado

`NO INICIADO` como piloto real. Existe narrativa y arquitectura estratégica.

### Pendiente completo

- definir alcance exacto del primer caso panameño.
- seleccionar un problema no crítico y verificable.
- mapa de stakeholders locales.
- taxonomía logística y territorial de Panamá.
- inventario de datasets públicos y autorizados.
- validación de licencias y condiciones de uso.
- fuentes en español e inglés.
- modelo de señales y riesgos específico.
- escenarios y briefings de demostración.
- metodología de actualización.
- revisión local por expertos.
- paquete para Ciudad del Saber e Innovar.
- propuesta de piloto controlado.
- acuerdos de confidencialidad y tratamiento de datos.
- métricas de éxito.
- soporte y formación.
- documentación clara de que no controla el Canal ni sistemas críticos.
- expansión posterior a Ports, Water, Energy, Airports, Cities y Health Infrastructure solo tras validación.

## 21. Orbyn Adaptive Agent Architecture, OAAA

### Propósito

Diseñar, ensamblar, evaluar y gobernar agentes adaptados a las necesidades de una empresa.

### Estado

`PARCIAL`. Existe dominio completo de blueprint y API de diseño hasta `IN_REVIEW`. El control plane de la API sigue en memoria.

### Lo construido

- blueprint con necesidad, rol, objetivo, tools, datos, acciones, autonomía, gates, logs, ARIA, rollback y disable.
- versiones, fingerprint e integrity hash.
- restricciones contra wildcards, autoaprobación, autoelevación, credenciales y autodespliegue.
- lifecycle de gobierno en el dominio.
- API para crear, leer, revisar y enviar a revisión.

### Pendiente crítico

- persistencia SQL de blueprints, versiones, decisiones y eventos.
- API de Aegis Clearance específica para el fingerprint del blueprint.
- API de ARIA vinculada al blueprint exacto.
- API de aprobación humana final.
- API de permisos Vigilance.
- gate integrado Clearance + ARIA + Human Approval + Vigilance.
- lifecycle API para `CLEARED`, `APPROVED`, `BLOCKED`, `SUSPENDED` y retirada.
- distinguir claramente activación de gobierno y despliegue runtime.
- Agent Registry persistente.
- Skill Registry.
- Tool Registry y allowlists.
- plantillas de agentes por caso de uso.
- generador asistido de blueprints desde una necesidad empresarial.
- comparación entre diseños alternativos.
- análisis de conflicto entre agentes.
- contratos de comunicación agente-agente.
- límites de memoria y contexto por agente.
- presupuestos de coste y rate limits.
- ownership y responsables.
- políticas de re-clearance tras cambios materiales.
- suspensión, retiro y archivado.
- incident linkage.
- monitorización y métricas por agente.
- sandbox de ejecución con datos sintéticos.
- harness de tools simuladas.
- packaging controlado de prompts, schemas y configuración.
- generación de código solo como propuesta revisable.
- proceso de publicación en repositorio privado.
- despliegue controlado mediante pipeline separado.
- rollback runtime.
- kill switch operativo.
- prohibición técnica de self-replication y self-deployment.
- pruebas de no escalada de privilegios.
- gestión de dependencias entre agentes.
- diseño de organizaciones multiagente.
- catálogo de blueprints reutilizables.

### Capacidad final buscada

```text
Necesidad empresarial
→ diagnóstico
→ propuesta de blueprint
→ revisión humana
→ Aegis Clearance
→ ARIA
→ Vigilance
→ aprobación nominal
→ sandbox
→ evidencia
→ despliegue controlado
→ monitorización
→ re-clearance o retirada
```

Esta cadena completa todavía no está construida.

## 22. Orbyn Synchronicity

### Propósito

Coordinar agentes, humanos, eventos, tareas y dependencias dentro de una organización agéntica.

### Estado

`NO INICIADO`.

### Pendiente completo

- event bus.
- workflow engine.
- triggers temporales y por evento.
- colas de trabajo.
- scheduler.
- contratos de handoff.
- coordinación agente-agente.
- coordinación humano-agente.
- prioridades y SLAs.
- manejo de concurrencia.
- resolución de conflictos.
- timeouts y retries.
- compensating actions y rollback.
- dead-letter queues.
- aprobación humana en puntos críticos.
- trazabilidad de ejecución.
- límites de coste y recursos.
- circuit breakers.
- dependencia entre casos.
- dashboards de procesos.
- simulación antes de activación.
- integración con Kernel, OAAA, Vigilance y Output Vault.

## 23. Orbyn Convergence

### Propósito

Interfaz futura para visualización avanzada, gemelos digitales, simulación espacial, formación e interacción inmersiva.

### Estado

`FUTURO`.

### Pendiente futuro

- modelos de digital twin no críticos.
- visualización 2D/3D.
- escenarios interactivos.
- formación y simulación.
- spatial interfaces.
- AR/VR solo cuando exista justificación comercial.
- integración con Atlas.
- representación de agentes y decisiones.
- controles de acceso y privacidad inmersiva.
- rendimiento y streaming.
- experiencias B2B/B2G.

No debe consumir recursos del MVP antes de que Atlas, Aegis y OAAA funcionen en pilotos reales.

# PARTE III · TODO LO QUE QUEDA POR HACER EN AEGIS

## 24. Aegis AI Readiness

### Estado

`NO INICIADO` como módulo de software completo.

### Pendiente

- intake de organización y AI Use Cases.
- inventario de IA, agentes, modelos, datos, proveedores y owners.
- clasificación de impacto y criticidad.
- madurez de gobierno.
- políticas y responsabilidades.
- evaluación de datos y privacidad.
- evaluación de supervisión humana.
- evaluación de incident readiness.
- evaluación de proveedores.
- mapa de gaps.
- roadmap 30-60-90.
- Dossier de Evidencias.
- reportes ejecutivos y técnicos.
- reevaluaciones periódicas.
- integración con Orbyn Readiness.
- conversión directa de hallazgos a Clearance cases.

## 25. Aegis Deployment Clearance

### Estado

`PARCIAL AVANZADO`. El motor determinista y la API existen.

### Pendiente

- persistir AI Use Cases y scorecards como entidades versionadas.
- historial de reevaluaciones.
- política de re-clearance por cambio de modelo, prompt, tool, datos o autonomía.
- formularios guiados.
- evidencia obligatoria por dimensión.
- policy packs por sector.
- override workflow documentado.
- especialistas externos y revisión cualificada.
- firma de reviewer.
- expiración del clearance.
- condiciones verificables y no solo textuales.
- checks automatizados de controles implementados.
- exportación PDF/DOCX.
- comparación entre versiones.
- dashboard de casos aptos, condicionados, bloqueados y caducados.
- integración automática con OAAA sin saltarse gates humanos.
- métricas de falsos positivos, falsos negativos y utilidad.
- gobernanza y versionado de la metodología.

## 26. Aegis Guardrails

### Estado

`PARCIAL`. Existe una biblioteca inicial de recomendaciones, no un sistema completo de controles.

### Pendiente

- guardrail objects persistentes.
- owner, estado, evidencia y fecha de revisión.
- controles técnicos, humanos y contractuales diferenciados.
- control library versionada.
- asignación por riesgo y sector.
- verificación de implementación.
- exceptions y compensating controls.
- policy-as-code.
- integración con Orbyn Guard y Vigilance.
- runtime checks.
- control effectiveness testing.
- reporting de cobertura.
- revalidación tras cambios.
- retiro de controles obsoletos.

## 27. Aegis Evidence

### Estado

`PARCIAL`. Existen outputs, EvidenceReference y Proof Receipts.

### Pendiente

- evidence graph completo.
- object storage privado.
- chain of custody.
- clasificación y redacción de evidencia.
- hashes y firmas.
- evidence bundles por caso.
- Dossier de Evidencias exportable.
- relaciones entre requisito, control, test, finding, decisión y aprobación.
- expiración y retención.
- legal hold.
- acceso por rol.
- watermarking de documentos sensibles.
- exportación PDF/DOCX/JSON.
- report templates para dirección, auditor, cliente y regulador.
- verificación de integridad.
- audit trail de descargas.
- integración con Nexus y Sovereign Vault.

## 28. Aegis Incident Readiness

### Estado

`NO INICIADO` como módulo operativo.

### Pendiente

- incident taxonomy.
- severidad y prioridad.
- owners y escalado.
- detección y triggers.
- integración con Vigilance y observabilidad.
- playbooks por tipo de incidente.
- kill switch.
- contención.
- revocación de permisos.
- suspensión de agentes.
- preservación de evidencia.
- comunicación interna y externa.
- decisiones de notificación.
- timeline del incidente.
- postmortem.
- corrective actions.
- re-clearance obligatoria.
- simulacros y tabletop exercises.
- métricas MTTA, MTTR y recurrencia.
- integración con soporte y contratos.

## 29. ARIA Adversarial Testing

### Estado

`PARCIAL`. El registro de campañas y findings existe como dominio, pero no existe API ni runner completo.

### Pendiente crítico

- API de campañas, runs, findings, resoluciones y receipts.
- persistencia SQL.
- test plan builder.
- dataset y corpus de pruebas.
- adapters por proveedor y modelo.
- sandbox aislado.
- harness de tools simuladas.
- prompt injection tests.
- data boundary pressure.
- role manipulation.
- tool permission drift.
- unsafe output.
- consistency under pressure.
- incident trigger and escalation.
- agent-to-agent attack tests.
- memory poisoning tests.
- exfiltration tests.
- rate and cost abuse tests.
- regression suites.
- scheduled reruns.
- severity calibration.
- reviewer workflow.
- dashboards y exportación.
- red-team manual para casos de mayor riesgo.
- prohibición de pruebas ofensivas sobre producción sin autorización expresa.
- vínculo automático con el fingerprint exacto de OAAA.

## 30. Aegis Atlas Assurance

### Estado

`NO INICIADO` como módulo independiente.

### Pendiente

- evaluar calidad y licencia de fuentes Atlas.
- verificar trazabilidad source → signal → risk → scenario → briefing.
- comprobar que inferencias no se presentan como hechos.
- validar sensibilidad.
- validar metodología y versión.
- revisar riesgos críticos.
- confirmar human review.
- generar Atlas Assurance Receipt.
- bloquear briefs con referencias rotas o evidencia insuficiente.
- revalidar tras cambios de fuentes o metodología.
- revisar límites territoriales y sectoriales.
- integrar con Aegis Clearance cuando un briefing alimente una acción o agente.

## 31. Aegis Tracking Assurance

### Estado

`NO INICIADO` dentro de esta nueva plataforma, aunque existe experiencia y documentación histórica del servicio.

### Pendiente

- intake de dominio, stack, CMP, GTM, GA4, Meta y Google Ads.
- registro de consent states.
- test plan de tracking.
- evidencia de Tag Assistant y Pixel Helper.
- verificación de eventos.
- duplicidades y secuencia de tags.
- Consent Mode v2.
- CMP communication.
- attribution gap analysis.
- report templates.
- Evidence Pack.
- client portal.
- seguimiento de remediación.
- retest.
- monitorización periódica.
- integración con Aegis Evidence.
- límites claros: auditoría técnica, no asesoría legal.

## 32. Aegis Training

### Estado

`NO INICIADO`.

### Pendiente

- currículum por rol.
- formación para dirección, owners, reviewers, developers y operadores.
- módulos de readiness, clearance, guardrails, incidentes y evidencia.
- ejercicios y casos.
- evaluación de comprensión.
- registro de asistencia.
- renovación periódica.
- materiales en español e inglés.
- integración con readiness y controls.
- certificados de formación, sin presentarlos como certificación regulatoria.

## 33. Aegis Critical Assurance

### Estado

`FUTURO Y BLOQUEADO`.

### Condiciones previas obligatorias

- equipo especializado.
- socios sectoriales.
- marco legal y contractual específico.
- threat model avanzado.
- seguridad y resiliencia demostradas.
- entornos aislados.
- pruebas independientes.
- seguro y responsabilidades definidos.
- auditoría externa.
- incident response maduro.

No debe conectarse Aegis, Atlas u OAAA a sistemas de control de infraestructura crítica durante el MVP ni los primeros pilotos.

# PARTE IV · CAPAS TRANSVERSALES PENDIENTES

## 34. Kernel Astrynn

### Estado

`PARCIAL`.

### Pendiente

- persistencia completa y migraciones.
- organizaciones, equipos y proyectos avanzados.
- policy registry.
- decision registry.
- risk registry global.
- dependency graph.
- presupuestos y límites.
- estados corporativos.
- eventos de dominio.
- API administrativa.
- event sourcing o historial equivalente.
- búsqueda y reporting.
- tenancy endurecido.
- archivado y retención.
- integración con todas las ramas.

## 35. DataForge

### Estado

`NO INICIADO` como plataforma, aunque existe definición estratégica.

### Pendiente

- source registry.
- dataset registry.
- evidence registry.
- data lineage.
- provenance.
- versioning.
- quality scores.
- schema registry.
- data contracts.
- semantic memory.
- retrieval indexes aislados.
- knowledge graph.
- pattern library.
- templates reutilizables.
- deletion and retention.
- observabilidad de calidad.
- integración con Atlas, Aegis, OAAA y Nexus.

## 36. Vigilance

### Estado

`PARCIAL`. Existe Permissions Layer de dominio.

### Pendiente

- API de grants y action requests.
- persistencia SQL.
- panel de permisos.
- adapters de enforcement.
- integración con secret manager externo.
- credenciales de corta duración emitidas por proveedor autorizado, no por el agente.
- aprobación y revocación.
- expiración.
- emergency disable operativo.
- audit logs runtime.
- policy violations.
- rate and cost limits.
- tool proxy o gateway.
- action receipts.
- alertas.
- integración con OAAA y Incident Readiness.
- pruebas de escalada de privilegios.

## 37. Output Vault

### Estado

`PARCIAL`. Existe el dominio, pero no una API y persistencia de producción completas.

### Pendiente

- persistencia SQL del catálogo.
- object storage de documentos.
- API.
- aprobación y rechazo.
- supersesión.
- firmas.
- exportación PDF, DOCX, Markdown y JSON.
- búsqueda.
- permisos.
- retención.
- legal hold.
- download audit.
- evidence links.
- UI.
- backup y restore.

## 38. Sovereign Vault

### Estado

`NO INICIADO` como servicio técnico.

### Pendiente

- clasificación de material soberano.
- repositorio privado independiente.
- cifrado fuerte.
- key management.
- accesos mínimos.
- break-glass procedure.
- audit logs.
- backup offline o equivalente.
- recuperación.
- documentación roja.
- credenciales y secretos fuera del repositorio de código.
- control de exportación y descarga.
- separación entre material comercial, operativo y estratégico.

## 39. Nexus y Proof Receipts

### Estado

`PARCIAL`. Los recibos existen en distintos módulos, pero no hay un Control Room unificado.

### Pendiente

- receipt registry global.
- relación entre caso, blueprint, clearance, ARIA, permisos, aprobación, output e incidente.
- integrity verification.
- timeline de decisiones.
- dashboards.
- control coverage.
- alertas de caducidad.
- evidencia faltante.
- receipt comparison.
- exportable assurance pack.
- auditor view.
- client view.
- executive view.

## 40. SSTO y Strategy Stack

### Estado

`NO INICIADO` como sistema operativo corporativo.

### Pendiente

- portfolio de iniciativas IA.
- owners y accountability.
- presupuesto.
- prioridades.
- policies.
- risk appetite.
- métricas.
- reporting al CEO.
- revisión trimestral.
- vendor governance.
- model registry corporativo.
- exceptions.
- training register.
- incident trends.
- decisions and evidence.
- integración con Aegis y Kernel.

# PARTE V · PRODUCTO, PILOTOS Y NEGOCIO

## 41. Diseño de producto y paquetes comerciales

### Pendiente

- definir paquetes finales y límites de cada servicio.
- Aegis AI Risk Snapshot.
- Aegis Deployment Clearance.
- Aegis Readiness.
- Atlas Briefing Pilot.
- Atlas + Aegis Pilot.
- OAAA Agent Blueprint Design.
- AgentOps mensual.
- Tracking Assurance.
- precios, alcance, entregables y exclusiones.
- contratos y SOW.
- criterios de reembolso cuando proceda.
- onboarding.
- soporte.
- SLAs.
- facturación.
- customer success.
- renewal and expansion.

## 42. Demo y casos de muestra

### Pendiente

- caso Aegis de bajo riesgo.
- caso Aegis con controles.
- caso Aegis bloqueado.
- caso Atlas no crítico.
- caso Orbyn Isthmus sintético.
- blueprint OAAA completo.
- campaña ARIA.
- permisos Vigilance.
- Proof Receipt pack.
- demo ejecutiva de 10 minutos.
- demo técnica de 30 minutos.
- walkthrough móvil.
- datasets y evidencias sintéticas.

## 43. Piloto interno

### Pendiente

- seleccionar un caso interno de Astrynn.
- usar solo datos sintéticos, públicos o aprobados.
- crear caso Kernel.
- crear blueprint OAAA.
- ejecutar Clearance.
- ejecutar ARIA.
- conceder permisos de sandbox.
- aprobar humanamente.
- ejecutar en entorno aislado.
- registrar outputs y evidencias.
- simular incidente y rollback.
- medir coste, calidad, tiempo y utilidad.
- documentar hallazgos.

## 44. Piloto externo controlado

### Gates previos

- repositorio privado.
- identidad de producción.
- RLS.
- persistencia completa.
- secretos gestionados.
- backups.
- observabilidad.
- frontend mínimo.
- términos, privacidad, DPA y SOW.
- security review.
- incident playbook.
- soporte definido.

### Ejecución pendiente

- seleccionar cliente de bajo riesgo.
- limitar usuarios y datos.
- sandbox.
- objetivos y métricas.
- aprobación del cliente.
- revisión periódica.
- cierre y evidence pack.

## 45. Panamá, Ciudad del Saber e Innovar

### Pendiente

- narrativa institucional final.
- one-page actualizado.
- deck.
- dossier técnico.
- dossier de riesgos y límites.
- demo Orbyn Isthmus.
- selección de partners.
- reuniones exploratorias.
- piloto no crítico.
- propuesta de Panama AI Operations Lab solo tras señales reales de demanda.
- definición de impacto local y empleo.
- presupuesto.
- propiedad intelectual y jurisdicción.
- modelo de colaboración.

## 46. Legal, privacidad y contractual

### Pendiente

- privacy notice.
- terms of service.
- DPA.
- subprocessor list.
- data retention policy.
- security policy.
- acceptable use policy.
- incident notification terms.
- AI limitations and disclaimers.
- no-certification disclaimer.
- IP ownership.
- confidentiality.
- pilot agreement.
- professional liability review.
- DPIA cuando corresponda.
- mapping regulatorio documentado y revisado.
- asesoramiento cualificado para sectores regulados.

# PARTE VI · ROADMAP PRIORIZADO

## 47. Fase A · Endurecer el núcleo

Prioridad inmediata:

1. API ARIA.
2. API Vigilance.
3. persistencia de OAAA, ARIA, Vigilance y Output Vault.
4. migraciones y esquema formal.
5. Row Level Security.
6. IdP de producción y MFA.
7. secret management.
8. backups y restore.
9. observabilidad.
10. frontend móvil mínimo.

### Exit criteria

- ningún módulo crítico en memoria.
- aislamiento probado entre organizaciones.
- identidad no basada en tokens estáticos de desarrollo.
- recuperación de datos probada.
- logs y alertas operativos.
- seguridad revisada.

## 48. Fase B · Flujo integrado de gobierno

Construir:

```text
Need Intake
→ OAAA Blueprint
→ Aegis Clearance
→ ARIA
→ Human Approval
→ Vigilance Grants
→ Sandbox Activation
→ Output Vault
→ Proof Receipt
→ Review
```

### Exit criteria

- ningún salto manual invisible.
- todas las versiones vinculadas por fingerprint.
- cambios materiales invalidan clearance, tests y permisos.
- rollback y disable probados.
- no existe autoaprobación.

## 49. Fase C · Alpha interna

- frontend mínimo.
- un caso Aegis.
- un caso Atlas.
- un blueprint OAAA.
- sandbox con tools simuladas.
- evidencia completa.
- simulacro de incidente.
- evaluación de costes.

### Exit criteria

- flujo repetible.
- cero findings críticos abiertos.
- owners y reviewers diferenciados.
- documentación y runbooks completos.

## 50. Fase D · Primer piloto externo

- cliente o partner de bajo riesgo.
- datos limitados.
- sin sistemas críticos.
- alcance contractual cerrado.
- métricas y criterios de parada.
- soporte y incident response.

### Exit criteria

- utilidad demostrada.
- evidencia aceptable para el cliente.
- seguridad sin incidentes graves.
- mejoras registradas.
- decisión explícita de continuar, rediseñar o detener.

## 51. Fase E · Orbyn Isthmus

- caso no crítico en Panamá.
- fuentes públicas y autorizadas.
- Atlas Briefing.
- Atlas Assurance.
- demo institucional.
- pilot agreement.

### Exit criteria

- stakeholder local comprometido.
- valor medible.
- narrativa verificable.
- ninguna promesa de control de infraestructura.

## 52. Fase F · Expansión de la familia Orbyn

Orden recomendado:

1. Orbyn Readiness.
2. Orbyn Forge.
3. Orbyn Guard.
4. Orbyn Data.
5. Orbyn Synchronicity.
6. packs sectoriales Atlas.
7. Convergence solo en fase futura.

## 53. Fase G · Escala comercial

- multi-tenancy maduro.
- billing.
- customer success.
- SLAs.
- partner program.
- plantillas sectoriales.
- integraciones aprobadas.
- observabilidad y soporte 24/7 solo si el modelo económico lo justifica.
- auditoría externa.

# PARTE VII · PROHIBICIONES Y NO OBJETIVOS

## 54. Prohibiciones actuales

- No introducir datos reales de clientes en el repositorio público.
- No guardar credenciales en GitHub, documentos, issues o screenshots.
- No exponer públicamente la API actual.
- No conectar agentes a infraestructura crítica.
- No permitir self-replication.
- No permitir self-deployment.
- No permitir autoelevación de permisos.
- No permitir autoaprobación.
- No permitir acciones destructivas sin aprobación explícita.
- No presentar `ACTIVE` como runtime real.
- No presentar `ALLOWED` como acción ya ejecutada.
- No presentar un Proof Receipt como certificación oficial.
- No afirmar cumplimiento legal automático.
- No presentar escenarios Atlas como predicciones ciertas.
- No iniciar Convergence antes de validar el núcleo comercial.

# PARTE VIII · CONTROL DEL ROADMAP

## 55. Regla para considerar un bloque terminado

Un módulo solo se considera terminado cuando:

1. existe especificación.
2. existe código.
3. existen pruebas.
4. existe persistencia cuando corresponde.
5. existe autenticación y autorización.
6. existe documentación.
7. existe evidencia y audit trail.
8. existe rollback.
9. existe monitorización.
10. ha pasado revisión de seguridad.
11. ha sido validado con usuarios.
12. no depende de afirmaciones no demostradas.

## 56. Fuente de verdad y control de cambios

- Este documento gobierna el roadmap de construcción.
- El Documento Maestro Integrado gobierna doctrina, posicionamiento y arquitectura empresarial.
- GitHub `main` refleja código aceptado.
- Las Pull Requests reflejan cambios revisables.
- GitHub Actions demuestra únicamente que lint y tests automatizados pasaron.
- Los Issues convierten este roadmap en unidades ejecutables.
- Toda modificación estratégica debe actualizar primero el documento maestro y después este roadmap.
- Toda modificación técnica material debe generar ADR, issue, branch, tests y PR.

## 57. Cómo verificar desde el móvil

1. Abrir `Sellynet/astrynn-devforge-gpt`.
2. Revisar `docs/BUILD_STATUS.md`.
3. Abrir **Pull requests** y filtrar por `Merged`.
4. Abrir **Actions** para confirmar CI verde.
5. Abrir **Issues** para ver el siguiente bloque.
6. Abrir `tests/` para comprobar comportamientos reales.
7. Abrir `docs/` para revisar límites.
8. No interpretar una descripción o issue como código ya construido.

## 58. Conclusión ejecutiva

Astrynn ya dispone de una base tecnológica y doctrinal seria para Kernel, Aegis Clearance, Orbyn Atlas, OAAA, ARIA, Vigilance y evidencia. Sin embargo, la mayor parte del camino hacia una organización agéntica comercial, persistente, segura y operativa todavía está por construir.

La prioridad no es añadir más nombres ni abrir más frentes. La prioridad es completar el circuito gobernado:

**necesidad → blueprint → clearance → pruebas → permisos → aprobación → sandbox → evidencia → monitorización → revisión.**

Después se expandirán Orbyn Forge, Readiness, Guard, Data, Synchronicity, Atlas sectorial e Isthmus. Convergence queda deliberadamente en el horizonte futuro.

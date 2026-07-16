# VERIFICATION.md · Bloque 0 · Verificación humana del prototipo

Fecha de apertura: 2026-07-16

Repositorio: `Sellynet/astrynn-devforge-gpt`

Estado global: `BLOQUE 0 PARCIALMENTE COMPLETADO · 16/16 ENDPOINTS + 22/22 CONTROLES NEGATIVOS + 20/20 PERSISTENCIA REINICIO VERIFICADOS`

## 1. Regla de evidencia

Estados permitidos:

- `FUNCIONA VERIFICADO`: ejecución reproducible completada y evidencia revisada.
- `FALLA`: el comportamiento observado contradice el resultado esperado.
- `DUDOSO`: evidencia incompleta, ambigua o capacidad no construida.
- `PENDIENTE`: prueba todavía no ejecutada.

Una CI verde no cierra por sí sola todo el Bloque 0. Siguen pendientes el README reproducible, PostgreSQL/Supabase, persistencia operativa OAAA, lectura humana de tests, revisión de gaps de Pull Requests y revisión humana nominal.

No se utilizaron datos reales, secretos ni credenciales de clientes.

## 2. Resumen de ejecuciones válidas

### R-002 · Primeros ocho endpoints

- Workflow: `Block 0 Human Verification`
- Run ID: `29487356386`
- Run number: `2`
- Python: `3.11.15`
- Ruff: `All checks passed!`
- pytest: `113 passed, 1 warning`
- Resultado: `8/8 FUNCIONA VERIFICADO`
- Artifact: `block0-human-verification-2`
- Artifact SHA-256: `4ed3836f406b6567cb775c0f30df54e3cc492f327f9757ec293d1cf9f60749ef`

Informe permanente:

`docs/verification/BLOCK0_FIRST_8_ENDPOINTS_2026-07-16.md`

### R-003 · Ocho endpoints restantes

- Workflow: `Block 0 Remaining Endpoint Verification`
- Run ID: `29494393775`
- Run number: `1`
- Python: `3.11.15`
- Ruff: `All checks passed!`
- pytest: `113 passed, 1 warning`
- Resultado: `8/8 FUNCIONA VERIFICADO`
- Artifact: `block0-remaining-endpoints-1`
- Artifact SHA-256: `7854959c7233498d78036777383a18a9beb2d84aace726d20d2f778496314bd7`

Informe permanente:

`docs/verification/BLOCK0_REMAINING_8_ENDPOINTS_2026-07-16.md`

### R-004 · Controles negativos deliberados

- Workflow: `Block 0 Deliberate Negative Verification`
- Run ID: `29496148880`
- Run number: `2`
- Commit evaluado: `883bcf5d93f9d0f7faa154dfb1d4439f699ed036`
- Fecha UTC: `2026-07-16T11:54:45Z`
- Python: `3.11.15`
- Ruff: `All checks passed!`
- pytest: `113 passed, 1 warning in 2.44s`
- Resultado: `22/22 FUNCIONA VERIFICADO`
- Artifact: `block0-negative-verification-2`
- Artifact ID: `8374449620`
- Artifact SHA-256: `2911df6146ed80f7919ff31051497632d993dd415941c04a253cb47e1d7e4f4a`

Informe permanente:

`docs/verification/BLOCK0_NEGATIVE_CONTROLS_2026-07-16.md`

### R-005 · Persistencia tras reiniciar Uvicorn

- Workflow: `Block 0 Restart Persistence Verification`
- Run ID: `29499245290`
- Run number: `5`
- Head de la rama: `7b5feda97ac744106cf689320627d2cf72fc32f9`
- Commit evaluado: `18cde36c0dd3d14e941ff88c274d53e38cfb4563`
- Fecha UTC: `2026-07-16T12:43:26Z`
- Python: `3.11.15`
- Ruff: `All checks passed!`
- pytest: `113 passed, 1 warning in 2.58s`
- Resultado: `20/20 FUNCIONA VERIFICADO`
- Artifact: `block0-restart-persistence-5`
- Artifact ID: `8375700175`
- Artifact SHA-256: `4bbfc58d7aa57bb1876dd00e102cb2c957a0c398d2b48e899321e3eabc39d7c0`
- SQLite SHA-256: `07714892ca70cd0b76fee4532618bb36c444c8656ebed6195fa905c8808c80fb`

Informe permanente:

`docs/verification/BLOCK0_RESTART_PERSISTENCE_2026-07-16.md`

## 3. Endpoints verificados

| ID | Endpoint | HTTP | Estado |
|---|---|---:|---|
| E-001 | `GET /health` | 200 | `FUNCIONA VERIFICADO` |
| E-002 | `GET /api/v1/me` | 200 | `FUNCIONA VERIFICADO` |
| E-003 | `POST /api/v1/cases` | 201 | `FUNCIONA VERIFICADO` |
| E-004 | `GET /api/v1/cases` | 200 | `FUNCIONA VERIFICADO` |
| E-005 | `GET /api/v1/cases/{case_id}` | 200 | `FUNCIONA VERIFICADO` |
| E-006 | `POST /api/v1/cases/{case_id}/transition` | 200 | `FUNCIONA VERIFICADO` |
| E-007 | `POST /api/v1/cases/{case_id}/approvals` | 201 | `FUNCIONA VERIFICADO` |
| E-008 | `POST /api/v1/aegis/cases/{case_id}/clearance/evaluate` | 200 | `FUNCIONA VERIFICADO` |
| E-009 | `POST /api/v1/aegis/cases/{case_id}/clearance/record` | 201 | `FUNCIONA VERIFICADO` |
| E-010 | `POST /api/v1/atlas/cases/{case_id}/briefing/build` | 200 | `FUNCIONA VERIFICADO` |
| E-011 | `POST /api/v1/atlas/cases/{case_id}/briefing/record` | 201 | `FUNCIONA VERIFICADO` |
| E-012 | `POST /api/v1/oaaa/cases/{case_id}/blueprints` | 201 | `FUNCIONA VERIFICADO` |
| E-013 | `GET /api/v1/oaaa/blueprints/{blueprint_id}` | 200 | `FUNCIONA VERIFICADO` |
| E-014 | `GET /api/v1/oaaa/blueprints/{blueprint_id}/versions` | 200 | `FUNCIONA VERIFICADO` |
| E-015 | `POST /api/v1/oaaa/blueprints/{blueprint_id}/revisions` | 201 | `FUNCIONA VERIFICADO` |
| E-016 | `POST /api/v1/oaaa/blueprints/{blueprint_id}/submit` | 200 | `FUNCIONA VERIFICADO` |

## 4. Controles negativos verificados

### Autenticación e identidad

- token ausente rechazado con 401;
- token inválido rechazado con 401;
- `actor_id`, `owner_id` y `organization_id` falsificables rechazados;
- identidad derivada del principal autenticado.

### Aislamiento y least privilege

- creación y lectura cross-organization rechazadas;
- lectura cross-organization de blueprint rechazada;
- segundo owner bloqueado sobre caso ajeno;
- viewer bloqueado para Aegis Evaluate.

### Separación de funciones

- autoaprobación bloqueada;
- owner bloqueado para activación;
- owner bloqueado para Aegis Record;
- owner bloqueado para Atlas Record.

### Estados y transiciones

- `DRAFT → ACTIVE` rechazado;
- envío OAAA duplicado rechazado;
- endpoint OAAA `activate` inexistente.

### Controles Aegis, Atlas y OAAA

- score 6 rechazado;
- specialist trigger fuerza revisión especializada;
- critical blocker impide `APTO`;
- Atlas rechaza referencias de fuente inexistentes;
- OAAA rechaza wildcards de tools;
- OAAA rechaza plan ARIA sin `INCIDENT_TRIGGER`.

## 5. Persistencia tras reinicio verificada

La ejecución utilizó dos procesos Uvicorn distintos y el mismo archivo SQLite.

Después de detener completamente el primer proceso y arrancar el segundo con `ASTRYNN_AUTO_CREATE_SCHEMA=false`, sobrevivieron sin cambios:

- case ID y estado `APPROVED`;
- versión interna Kernel `5`;
- cuatro eventos con los mismos IDs;
- una aprobación con el mismo ID;
- cuatro outputs con los mismos IDs;
- seis evidencias con los mismos IDs.

Las filas físicas posteriores coincidieron con el baseline previo:

```json
{
  "cases": 1,
  "events": 4,
  "approvals": 1,
  "outputs": 4,
  "evidence": 6
}
```

El caso recuperado pudo evaluarse de nuevo con Aegis y produjo `APTO` con puntuación total `9`.

### Frontera OAAA

El blueprint operativo anterior devolvió `404 Blueprint not found` después del reinicio.

Esto confirma:

- `estado operativo OAAA`: volátil en `InMemoryAgentBlueprintRepository`;
- `rastro de auditoría OAAA`: persistente en Kernel.

Persistieron dos outputs `OAAA_AGENT_BLUEPRINT` y las evidencias de Output Vault y OAAA correspondientes a las versiones 1 y 2.

## 6. Evidencia funcional confirmada

### Kernel y autorización

- identidad derivada del token;
- creación, listado y lectura del caso;
- transiciones gobernadas;
- aprobación independiente;
- aislamiento organizativo y de ownership;
- persistencia SQLite entre procesos para casos, eventos, aprobaciones, outputs y evidencias.

### Aegis

- evaluación determinista;
- fingerprints de entrada;
- registro de Clearance Report y Proof Receipt;
- specialist triggers y critical blockers prevalecen sobre el score;
- outputs y evidencia sobreviven al reinicio;
- no hay aprobación, activación o despliegue como efecto secundario.

### Atlas

- FACT, INFERENCE, ASSUMPTION y RECOMMENDATION tipadas;
- registro de briefing con output y evidencia;
- referencias rotas rechazadas;
- producción final separada del owner;
- outputs y evidencia sobreviven al reinicio.

### OAAA

- blueprint versionado de `DRAFT` a `IN_REVIEW` dentro del proceso;
- safety fingerprint e integrity hash;
- ownership y organización controlados;
- wildcards y planes ARIA incompletos rechazados;
- sin endpoint de activación;
- artefactos y evidencias de auditoría durables;
- repositorio operativo de blueprints todavía volátil.

## 7. Límites y hallazgos abiertos

### README

Estado: `FALLA · DOCUMENTACIÓN INSUFICIENTE`

El README permite instalar y ejecutar Ruff/pytest, pero no documenta todavía el recorrido completo desde clone hasta API operativa, tokens, Uvicorn, SQLite, Swagger, reinicio y persistencia.

### OAAA operativo

Estado: `DUDOSO · CAPACIDAD PRODUCTIVA NO CONSTRUIDA`

El control plane declara `in-memory-development` y el blueprint operativo se pierde al reiniciar. El rastro de auditoría sí es durable, pero no sustituye a una persistencia operativa de blueprints y versiones.

### Warning de dependencias

Estado: `DUDOSO · DEUDA TÉCNICA NO BLOQUEANTE`

pytest registra un `StarletteDeprecationWarning` relacionado con `httpx` y `starlette.testclient`.

### Intentos de harness descartados

- Run negativo `29495923583`: criterio textual demasiado estricto para HTTP 403. Corregido.
- Run reinicio `29498525073`: SQLite contaminó pytest y se intentaron leer campos no expuestos por `CaseResponse`. Corregido.
- Run reinicio `29498940953`: esperaba 2 outputs y 2 evidencias, pero OAAA añadió rastro durable y produjo 4 outputs y 6 evidencias. Corregido mediante baseline dinámico.

Clasificación común: `FALLA DEL HARNESS · CORREGIDA`.

## 8. Pendientes para cerrar el Bloque 0

1. Corregir el README y repetir el levantamiento siguiendo solo esa documentación.
2. Construir persistencia operativa OAAA y verificar su supervivencia tras reinicio.
3. Repetir persistencia Kernel con PostgreSQL/Supabase.
4. Leer manualmente los tests y valorar su calidad, relevancia y cobertura real.
5. Revisar gaps entre Pull Requests y commits.
6. Resolver o aceptar formalmente el warning de Starlette/httpx.
7. Obtener revisión humana nominal de la evidencia.

## 9. Conclusión

Los 16 endpoints, los 22 controles negativos y los 20 controles de persistencia tras reinicio quedan como `FUNCIONA VERIFICADO` dentro de ejecuciones reproducibles de GitHub Actions.

La persistencia SQLite del Kernel está demostrada entre procesos distintos. OAAA conserva artefactos y evidencias de auditoría, pero no conserva todavía el blueprint operativo.

Esto no demuestra identidad productiva, PostgreSQL/Supabase, concurrencia, runtime de agentes, integraciones reales, cumplimiento ni certificación.

El siguiente tramo obligatorio es corregir el README o construir persistencia operativa OAAA. Según ADR-002, la prioridad inmediata debe ser cerrar primero la reproducibilidad documental.
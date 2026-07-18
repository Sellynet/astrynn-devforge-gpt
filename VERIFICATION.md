# VERIFICATION.md · Bloque 0 · Verificación del prototipo

Fecha de apertura: 2026-07-16  
Última actualización: 2026-07-18

Repositorio: `Sellynet/astrynn-devforge-gpt`

Estado global: `BLOQUE 0 PARCIALMENTE COMPLETADO · PASADA HUMANA SWAGGER + README CLEAN-ROOM + 16/16 ENDPOINTS + 22/22 CONTROLES NEGATIVOS + 20/20 PERSISTENCIA REINICIO VERIFICADOS`

## 1. Regla de evidencia

Estados permitidos:

- `FUNCIONA VERIFICADO`: ejecución reproducible completada y evidencia revisada.
- `FALLA`: el comportamiento observado contradice el resultado esperado.
- `DUDOSO`: evidencia incompleta, ambigua o capacidad no construida.
- `PENDIENTE`: prueba todavía no ejecutada.

Una CI verde no cierra por sí sola todo el Bloque 0. La pasada humana nominal en Swagger ya está completada. Continúan pendientes PostgreSQL/Supabase, persistencia operativa OAAA, lectura humana de tests, revisión de gaps entre Pull Requests y commits, resolución o aceptación formal del warning y revisión humana nominal de la evidencia global.

No se utilizaron datos reales, secretos ni credenciales de clientes.

## 2. Resumen de ejecuciones válidas

### R-002 · Primeros ocho endpoints automatizados

- Workflow: `Block 0 Human Verification`
- Run ID: `29487356386`
- Run number: `2`
- Python: `3.11.15`
- Ruff: `All checks passed!`
- pytest: `113 passed, 1 warning`
- Resultado: `8/8 FUNCIONA VERIFICADO`
- Artifact: `block0-human-verification-2`
- Artifact SHA-256: `4ed3836f406b6567cb775c0f30df54e3cc492f327f9757ec293d1cf9f60749ef`
- Informe: `docs/verification/BLOCK0_FIRST_8_ENDPOINTS_2026-07-16.md`

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
- Informe: `docs/verification/BLOCK0_REMAINING_8_ENDPOINTS_2026-07-16.md`

### R-004 · Controles negativos deliberados

- Workflow: `Block 0 Deliberate Negative Verification`
- Run ID: `29496148880`
- Run number: `2`
- Commit evaluado: `883bcf5d93f9d0f7faa154dfb1d4439f699ed036`
- Python: `3.11.15`
- Ruff: `All checks passed!`
- pytest: `113 passed, 1 warning in 2.44s`
- Resultado: `22/22 FUNCIONA VERIFICADO`
- Artifact: `block0-negative-verification-2`
- Artifact SHA-256: `2911df6146ed80f7919ff31051497632d993dd415941c04a253cb47e1d7e4f4a`
- Informe: `docs/verification/BLOCK0_NEGATIVE_CONTROLS_2026-07-16.md`

### R-005 · Persistencia tras reiniciar Uvicorn

- Workflow: `Block 0 Restart Persistence Verification`
- Run ID: `29499245290`
- Run number: `5`
- Python: `3.11.15`
- Ruff: `All checks passed!`
- pytest: `113 passed, 1 warning in 2.58s`
- Resultado: `20/20 FUNCIONA VERIFICADO`
- Artifact: `block0-restart-persistence-5`
- Artifact SHA-256: `4bbfc58d7aa57bb1876dd00e102cb2c957a0c398d2b48e899321e3eabc39d7c0`
- SQLite SHA-256: `07714892ca70cd0b76fee4532618bb36c444c8656ebed6195fa905c8808c80fb`
- Informe: `docs/verification/BLOCK0_RESTART_PERSISTENCE_2026-07-16.md`

### R-006 · README clean-room

- Workflow: `Block 0 README Clean-room Verification`
- Run ID: `29504297700`
- Run number: `1`
- Rama clonada: `verification/block-0-readme-cleanroom`
- Python: `3.11.15`
- Ruff: `All checks passed!`
- pytest: `113 passed, 1 warning in 2.55s`
- Resultado: `README CLEAN-ROOM + 8/8 FUNCIONA VERIFICADO`
- Artifact: `block0-readme-cleanroom-1`
- Artifact SHA-256: `9e8102a0de3a34d0a8426a2418b063a585e31774f6519afc9aca30e5712fae86`
- Informe: `docs/verification/BLOCK0_README_CLEANROOM_2026-07-16.md`

Clasificación del README: `FUNCIONA VERIFICADO · CLEAN-ROOM AUTOMATIZADO`.

### R-007 · Pasada humana nominal en Swagger

- Fecha: `2026-07-18`
- Entorno: GitHub Codespaces `cautious-waffle`
- Rama observada: `main`
- Python: `3.12.1`
- Navegador: Chrome sobre Windows 11
- Ruff: `All checks passed!`
- pytest: `113 passed, 1 warning in 4.37s`
- Swagger: puerto privado reenviado `8000`
- Resultado: `8/8 FUNCIONA VERIFICADO · OBSERVACIÓN HUMANA NOMINAL`
- Case ID sintético: `b428c5ea-0dd6-4e51-890c-176f6ea34eac`
- Aprobación observada: `APPROVE_WITH_CONDITIONS`
- Aegis observado: `APTO`, `total_score=9`
- Informe: `docs/verification/BLOCK0_HUMAN_SWAGGER_2026-07-18.md`

La observación humana nominal en Swagger queda como `FUNCIONA VERIFICADO`.

## 3. Endpoints verificados

| ID | Endpoint | HTTP | Automático | Humano Swagger |
|---|---|---:|---|---|
| E-001 | `GET /health` | 200 | `FUNCIONA VERIFICADO` | `FUNCIONA VERIFICADO` |
| E-002 | `GET /api/v1/me` | 200 | `FUNCIONA VERIFICADO` | `FUNCIONA VERIFICADO` |
| E-003 | `POST /api/v1/cases` | 201 | `FUNCIONA VERIFICADO` | `FUNCIONA VERIFICADO` |
| E-004 | `GET /api/v1/cases` | 200 | `FUNCIONA VERIFICADO` | `FUNCIONA VERIFICADO` |
| E-005 | `GET /api/v1/cases/{case_id}` | 200 | `FUNCIONA VERIFICADO` | `FUNCIONA VERIFICADO` |
| E-006 | `POST /api/v1/cases/{case_id}/transition` | 200 | `FUNCIONA VERIFICADO` | `FUNCIONA VERIFICADO` |
| E-007 | `POST /api/v1/cases/{case_id}/approvals` | 201 | `FUNCIONA VERIFICADO` | `FUNCIONA VERIFICADO` |
| E-008 | `POST /api/v1/aegis/cases/{case_id}/clearance/evaluate` | 200 | `FUNCIONA VERIFICADO` | `FUNCIONA VERIFICADO` |
| E-009 | `POST /api/v1/aegis/cases/{case_id}/clearance/record` | 201 | `FUNCIONA VERIFICADO` | `NO INCLUIDO EN PASADA HUMANA` |
| E-010 | `POST /api/v1/atlas/cases/{case_id}/briefing/build` | 200 | `FUNCIONA VERIFICADO` | `NO INCLUIDO EN PASADA HUMANA` |
| E-011 | `POST /api/v1/atlas/cases/{case_id}/briefing/record` | 201 | `FUNCIONA VERIFICADO` | `NO INCLUIDO EN PASADA HUMANA` |
| E-012 | `POST /api/v1/oaaa/cases/{case_id}/blueprints` | 201 | `FUNCIONA VERIFICADO` | `NO INCLUIDO EN PASADA HUMANA` |
| E-013 | `GET /api/v1/oaaa/blueprints/{blueprint_id}` | 200 | `FUNCIONA VERIFICADO` | `NO INCLUIDO EN PASADA HUMANA` |
| E-014 | `GET /api/v1/oaaa/blueprints/{blueprint_id}/versions` | 200 | `FUNCIONA VERIFICADO` | `NO INCLUIDO EN PASADA HUMANA` |
| E-015 | `POST /api/v1/oaaa/blueprints/{blueprint_id}/revisions` | 201 | `FUNCIONA VERIFICADO` | `NO INCLUIDO EN PASADA HUMANA` |
| E-016 | `POST /api/v1/oaaa/blueprints/{blueprint_id}/submit` | 200 | `FUNCIONA VERIFICADO` | `NO INCLUIDO EN PASADA HUMANA` |

## 4. Resultado de la pasada humana

La persona operadora observó en Swagger:

- salud de la API y límites declarados;
- identidad `CASE_OWNER` derivada del token;
- creación y recuperación del caso sintético;
- presencia del caso en el listado;
- transición `DRAFT → IN_REVIEW`;
- cambio de identidad a `REVIEWER`;
- aprobación `APPROVE_WITH_CONDITIONS`;
- regreso a `CASE_OWNER`;
- evaluación Aegis `APTO` con puntuación total `9`.

### Fricción Swagger

El primer intento de aprobación devolvió HTTP 422 porque el editor contenía dos objetos JSON concatenados: el ejemplo generado y el cuerpo introducido. La sustitución completa por un único objeto válido produjo HTTP 201.

Clasificación: `FRICCIÓN DE INTERFAZ / ENTRADA HUMANA · NO FALLO DE API`.

La búsqueda textual del navegador tampoco localizó de forma fiable algunas etiquetas de endpoints dentro de Swagger. Se navegó directamente por la sección `kernel`.

## 5. Controles negativos verificados

### Autenticación e identidad

- token ausente e inválido rechazados con 401;
- spoofing de `actor_id`, `owner_id` y `organization_id` rechazado;
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

### Estados y validaciones

- `DRAFT → ACTIVE` rechazado;
- envío OAAA duplicado rechazado;
- endpoint OAAA `activate` inexistente;
- score fuera de rango rechazado;
- specialist trigger fuerza revisión especializada;
- critical blocker impide `APTO`;
- Atlas rechaza referencias rotas;
- OAAA rechaza wildcards y planes ARIA incompletos.

## 6. Persistencia tras reinicio

Sobrevivieron con el mismo SQLite:

- case ID y estado `APPROVED`;
- versión interna Kernel `5`;
- cuatro eventos;
- una aprobación;
- cuatro outputs;
- seis evidencias.

Filas físicas posteriores:

```json
{
  "cases": 1,
  "events": 4,
  "approvals": 1,
  "outputs": 4,
  "evidence": 6
}
```

El caso recuperado volvió a producir `APTO` con puntuación total `9`.

### Frontera OAAA

- estado operativo OAAA: volátil en `InMemoryAgentBlueprintRepository`;
- rastro de auditoría OAAA: persistente en Kernel;
- el blueprint operativo devuelve `404 Blueprint not found` tras reiniciar;
- outputs y evidencias de sus versiones permanecen.

## 7. README y reproducibilidad

El README contiene requisitos, clonación, entorno virtual, instalación, Ruff, pytest, tokens sintéticos, SQLite, Uvicorn, Swagger, primeros ocho endpoints, reinicio, persistencia, plantilla de fricciones y límites productivos.

El workflow extrajo el bloque ejecutable directamente del README y completó el recorrido desde un clon limpio.

Fricciones conocidas:

- `DUDOSO · DEUDA TÉCNICA NO BLOQUEANTE`: `StarletteDeprecationWarning` relacionado con `httpx` y `starlette.testclient`.
- `DUDOSO · COSMÉTICO NO BLOQUEANTE`: presentación incorrecta de la ruta absoluta de evidencias en el mensaje final del runner, sin pérdida de archivos.
- `RESUELTO`: pasada humana nominal en Swagger desde un ordenador físico.

## 8. Hallazgos abiertos

### OAAA operativo

Estado: `DUDOSO · CAPACIDAD PRODUCTIVA NO CONSTRUIDA`.

El blueprint operativo se pierde al reiniciar. El rastro durable no sustituye la persistencia operativa de blueprints y versiones.

### PostgreSQL/Supabase

Estado: `PENDIENTE`.

No se han verificado migraciones, RLS, backups, secretos seguros ni persistencia contra PostgreSQL/Supabase.

### Warning de dependencias

Estado: `DUDOSO · DEUDA TÉCNICA NO BLOQUEANTE`.

Debe resolverse o aceptarse formalmente con versión y fecha de revisión.

### Lectura humana de tests y evidencia global

Estado: `PENDIENTE`.

La ejecución humana de Swagger no sustituye la lectura crítica del código de tests ni la revisión nominal del conjunto completo de evidencias.

## 9. Intentos descartados o corregidos

- Run negativo `29495923583`: criterio textual demasiado estricto para HTTP 403. Corregido.
- Run reinicio `29498525073`: SQLite contaminó pytest y se intentaron leer campos no expuestos. Corregido.
- Run reinicio `29498940953`: expectativa fija de artefactos incorrecta. Corregido con baseline dinámico.
- Primer intento humano de aprobación: dos objetos JSON concatenados en Swagger, HTTP 422. Corregido mediante reemplazo completo; repetición HTTP 201.

Los tres primeros son `FALLA DEL HARNESS · CORREGIDA`. El último es `FRICCIÓN DE INTERFAZ / ENTRADA HUMANA · CORREGIDA`.

## 10. Pendientes para cerrar el Bloque 0 completo

1. Construir persistencia operativa OAAA y verificar su supervivencia.
2. Repetir persistencia Kernel con PostgreSQL/Supabase.
3. Leer manualmente los tests y valorar calidad, relevancia y cobertura real.
4. Revisar gaps entre Pull Requests y commits.
5. Resolver o aceptar formalmente el warning de Starlette/httpx.
6. Obtener revisión humana nominal de la evidencia global.

La pasada humana Swagger deja de figurar como pendiente.

## 11. Conclusión

La reproducibilidad documental del README, los 16 endpoints automáticos, los 22 controles negativos y los 20 controles de persistencia quedan como `FUNCIONA VERIFICADO`.

Los primeros ocho endpoints también quedan como `FUNCIONA VERIFICADO · OBSERVACIÓN HUMANA NOMINAL` en Swagger.

Esto no demuestra todavía identidad productiva, PostgreSQL/Supabase, persistencia operativa OAAA, concurrencia, runtime de agentes, integraciones reales, cumplimiento ni certificación.

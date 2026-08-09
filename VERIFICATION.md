# VERIFICATION.md v2.2 · Bloque 0 · Verificación del prototipo

Fecha de apertura: 2026-07-16

Última actualización: 2026-07-29

Versión documental: `2.2`

Repositorio: `Sellynet/astrynn-devforge-gpt`

Estado global: `BLOQUE 0 PARCIALMENTE COMPLETADO · PASADA HUMANA SWAGGER + README CLEAN-ROOM + 16/16 ENDPOINTS + 22/22 CONTROLES NEGATIVOS + 20/20 PERSISTENCIA REINICIO + LECTURA CRÍTICA 114/114 TESTS VERIFICADOS + OUTPUT VAULT OWNER_ID P0 RESUELTO + WARNING STARLETTE/HTTPX RESUELTO + AUDITORÍA PR/COMMIT 9/9 CERRADA`

## 1. Regla de evidencia

Estados permitidos:

- `FUNCIONA VERIFICADO`: ejecución reproducible completada y evidencia revisada.
- `FALLA`: el comportamiento observado contradice el resultado esperado.
- `DUDOSO`: evidencia incompleta, ambigua o capacidad no construida.
- `PENDIENTE`: prueba todavía no ejecutada.

Una CI verde no cierra por sí sola todo el Bloque 0. La pasada humana nominal en Swagger, la lectura crítica individual de los 114 tests y la auditoría de gaps entre issues, Pull Requests y commits están completadas. La invariante P0 de identidad de Output Vault y el warning Starlette/httpx quedan resueltos en la rama `fix/output-vault-owner-invariant`. Continúan pendientes PostgreSQL/Supabase, persistencia operativa OAAA, los demás huecos prioritarios de cobertura y la revisión humana nominal de la evidencia global.

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


### R-008 · Invariante de propietario Output Vault y migración a httpx2

- Fecha: `2026-07-25`
- Rama: `fix/output-vault-owner-invariant`
- Python: `3.12.1`
- Ruff local: `0.15.22` · `All checks passed!`
- Ruff instalación limpia: `0.16.0` · `All checks passed!`
- Output Vault: `7 passed`
- Suite completa: `114 passed`
- Warnings: `0`
- Statements: `2822/3092` · `91.27 %`
- Branches: `372/576` · `64.58 %`
- Cobertura combinada: `87.08 %`
- FastAPI: `0.139.2`
- Starlette: `1.3.1`
- httpx: `0.28.1`
- httpx2: `2.7.0`
- Resultado: `FUNCIONA VERIFICADO · REGRESIÓN LOCAL + INSTALACIÓN LIMPIA`

`OutputVaultService.create_draft()` comprueba ahora que el `owner_id`
suministrado coincide con el propietario del caso Kernel antes de construir
o persistir el artefacto.

La prueba negativa demuestra que un intento con un propietario distinto:

- lanza `VaultApprovalError`;
- no crea versiones en Output Vault;
- no crea outputs en Kernel;
- no crea evidencias residuales.

La prueba fue ejecutada inicialmente contra la implementación sin corregir
y falló porque la operación no era rechazada. Después de aplicar la
invariante, Output Vault pasó `7/7` y la suite completa pasó `114/114`.

El `StarletteDeprecationWarning` quedó resuelto mediante la incorporación
reproducible de `httpx2==2.7.0`. La instalación desde una
venv temporal limpia completó Ruff y los 114 tests sin warnings. No se
silenció ni filtró el warning.

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

- `RESUELTO`: `StarletteDeprecationWarning` eliminado mediante `httpx2==2.7.0` y reproducido desde una instalación limpia sin filtros de warnings.
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

Estado: `FUNCIONA VERIFICADO · RESUELTO`.

El warning de compatibilidad entre Starlette `1.3.1` y httpx `0.28.1` quedó eliminado incorporando `httpx2==2.7.0`. La solución fue reproducida en una venv limpia con Ruff verde, `114 passed` y cero warnings. No se utilizaron filtros, exclusiones ni silenciamiento.

### Lectura humana de tests

Estado: `FUNCIONA VERIFICADO · 114/114 TESTS CLASIFICADOS`.

La auditoría v2.1 mantiene la lectura individual de las 113 funciones originales e incorpora la nueva prueba de regresión. El conjunto resultante alcanza 114 funciones de test contrastadas con las rutas de código instrumentadas. El resultado, la matriz completa y los huecos detectados figuran en la sección 11.

### Evidencia global

Estado: `PENDIENTE`.

La lectura crítica de la suite no sustituye la revisión humana nominal del conjunto completo de artefactos e informes de evidencia.

## 9. Intentos descartados o corregidos

- Run negativo `29495923583`: criterio textual demasiado estricto para HTTP 403. Corregido.
- Run reinicio `29498525073`: SQLite contaminó pytest y se intentaron leer campos no expuestos. Corregido.
- Run reinicio `29498940953`: expectativa fija de artefactos incorrecta. Corregido con baseline dinámico.
- Primer intento humano de aprobación: dos objetos JSON concatenados en Swagger, HTTP 422. Corregido mediante reemplazo completo; repetición HTTP 201.

Los tres primeros son `FALLA DEL HARNESS · CORREGIDA`. El último es `FRICCIÓN DE INTERFAZ / ENTRADA HUMANA · CORREGIDA`.

## 10. Pendientes para cerrar el Bloque 0 completo

1. Construir persistencia operativa OAAA y verificar su supervivencia.
2. Repetir persistencia Kernel con PostgreSQL/Supabase.
3. Continuar convirtiendo los huecos P0 restantes en pruebas de regresión.
4. Obtener revisión humana nominal de la evidencia global.

La pasada humana Swagger, la lectura crítica de los 114 tests y la auditoría de gaps entre issues, Pull Requests y commits dejan de figurar como pendientes.

## 11. Auditoría crítica de la suite · VERIFICATION.md v2.1

### Alcance y método

La auditoría se realizó sobre el commit `d8564d201be5bc4c5465bcfea674b52fae99c35b` de `main`. La unidad clasificada es cada función `test_*` recogida por pytest: 113 funciones y 113 casos ejecutados.

Cada test fue leído completo y contrastado con la lógica de aplicación a la que llama. La clasificación binaria aplicada es:

- `SUSTANCIAL`: verifica al menos un comportamiento material de dominio, estado, seguridad, aislamiento, separación de funciones, integridad, persistencia, caso límite o fallo esperado. Una respuesta HTTP negativa cuenta como sustancial cuando demuestra que una operación material queda bloqueada.
- `TRIVIAL`: se limita a disponibilidad, un valor estático, conformidad estructural o un HTTP 200 sin comprobar semántica ni efectos.

Los dos tests de salud se clasifican como sustanciales porque no se limitan a comprobar HTTP 200: verifican el modo de autenticación y la frontera explícita de persistencia OAAA comunicada por la API. La clasificación `SUSTANCIAL` no significa que el test sea exhaustivo, resistente a mutaciones o suficiente para cerrar por sí solo el riesgo correspondiente.

### Ejecución auxiliar de auditoría

- Fecha: `2026-07-23`
- Python: `3.12.13`
- pytest: `113 passed`
- Warning: `1 StarletteDeprecationWarning` relacionado con `httpx` y `starlette.testclient`
- Cobertura de statements: `91.18 %` (`2.823/3.096` líneas ejecutables)
- Cobertura de branches: `64.85 %` (`380/586`)
- Cobertura combinada reportada: `86.99 %`
- Resultado: `FUNCIONA VERIFICADO · EJECUCIÓN LOCAL AUXILIAR`

La medición se ejecutó con las dependencias no fijadas que resolvía el proyecto en la fecha de auditoría. Complementa, pero no sustituye, los artefactos de CI ya registrados.


### Ejecución de regresión v2.1

- Fecha: `2026-07-25`
- Rama: `fix/output-vault-owner-invariant`
- pytest Output Vault: `7 passed`
- pytest completo: `114 passed`
- Warnings tras incorporar httpx2: `0`
- Ruff local: `0.15.22` · `All checks passed!`
- Ruff instalación limpia: `0.16.0` · `All checks passed!`
- Cobertura de statements: `91.27 %` (`2822/3092`)
- Cobertura de branches: `64.58 %` (`372/576`)
- Cobertura combinada: `87.08 %`
- Resultado: `FUNCIONA VERIFICADO · REGRESIÓN LOCAL Y CLEAN ENVIRONMENT`

### Resultado cuantitativo

| Clasificación | Tests | Porcentaje |
|---|---:|---:|
| `SUSTANCIAL` | 112 | 98,25 % |
| `TRIVIAL` | 2 | 1,75 % |
| **Total** | **114** | **100,00 %** |

Los dos tests triviales son:

1. `test_core.py::test_hello`: compara una cadena estática y no ejerce reglas, estado ni integración.
2. `tests/test_sqlalchemy_repository.py::test_sqlalchemy_repository_satisfies_kernel_contract`: comprueba conformidad estructural con el protocolo y una etiqueta estática, pero no ejerce persistencia. Los otros seis tests del mismo archivo sí prueban comportamiento real.

### Resumen por archivo

| Archivo | Total | Sustanciales | Triviales |
|---|---:|---:|---:|
| `test_core.py` | 1 | 0 | 1 |
| `tests/test_aegis_api.py` | 8 | 8 | 0 |
| `tests/test_aegis_clearance.py` | 9 | 9 | 0 |
| `tests/test_api.py` | 14 | 14 | 0 |
| `tests/test_api_persistence.py` | 1 | 1 | 0 |
| `tests/test_aria.py` | 7 | 7 | 0 |
| `tests/test_atlas.py` | 7 | 7 | 0 |
| `tests/test_atlas_api.py` | 11 | 11 | 0 |
| `tests/test_auth.py` | 5 | 5 | 0 |
| `tests/test_kernel.py` | 6 | 6 | 0 |
| `tests/test_oaaa_api.py` | 13 | 13 | 0 |
| `tests/test_oaaa_blueprint.py` | 10 | 10 | 0 |
| `tests/test_output_vault.py` | 7 | 7 | 0 |
| `tests/test_sqlalchemy_repository.py` | 7 | 6 | 1 |
| `tests/test_vigilance.py` | 8 | 8 | 0 |
| **Total** | **114** | **112** | **2** |

### Matriz individual 114/114

| ID | Test | Clasificación |
|---|---|---|
| T-001 | `test_core.py::test_hello` | `TRIVIAL` |
| T-002 | `tests/test_aegis_api.py::test_owner_evaluates_own_case_without_recording` | `SUSTANCIAL` |
| T-003 | `tests/test_aegis_api.py::test_same_input_produces_same_fingerprint` | `SUSTANCIAL` |
| T-004 | `tests/test_aegis_api.py::test_reviewer_records_clearance_report_and_evidence` | `SUSTANCIAL` |
| T-005 | `tests/test_aegis_api.py::test_owner_cannot_record_final_clearance` | `SUSTANCIAL` |
| T-006 | `tests/test_aegis_api.py::test_specialist_trigger_overrides_low_score` | `SUSTANCIAL` |
| T-007 | `tests/test_aegis_api.py::test_critical_blocker_returns_no_apto` | `SUSTANCIAL` |
| T-008 | `tests/test_aegis_api.py::test_viewer_cannot_evaluate_and_other_org_cannot_access` | `SUSTANCIAL` |
| T-009 | `tests/test_aegis_api.py::test_invalid_score_is_rejected` | `SUSTANCIAL` |
| T-010 | `tests/test_aegis_clearance.py::test_scores_require_integers_between_zero_and_five` | `SUSTANCIAL` |
| T-011 | `tests/test_aegis_clearance.py::test_low_risk_case_is_apto` | `SUSTANCIAL` |
| T-012 | `tests/test_aegis_clearance.py::test_medium_risk_case_requires_controls` | `SUSTANCIAL` |
| T-013 | `tests/test_aegis_clearance.py::test_high_aggregate_risk_is_not_ready` | `SUSTANCIAL` |
| T-014 | `tests/test_aegis_clearance.py::test_specialist_trigger_overrides_low_score` | `SUSTANCIAL` |
| T-015 | `tests/test_aegis_clearance.py::test_maximum_critical_dimension_blocks_deployment` | `SUSTANCIAL` |
| T-016 | `tests/test_aegis_clearance.py::test_concentrated_high_risk_requires_controls_even_with_low_total` | `SUSTANCIAL` |
| T-017 | `tests/test_aegis_clearance.py::test_input_fingerprint_is_deterministic` | `SUSTANCIAL` |
| T-018 | `tests/test_aegis_clearance.py::test_record_creates_review_artifact_and_evidence_without_activation` | `SUSTANCIAL` |
| T-019 | `tests/test_api.py::test_health_is_public_but_reports_authentication_mode` | `SUSTANCIAL` |
| T-020 | `tests/test_api.py::test_protected_endpoint_requires_bearer_token` | `SUSTANCIAL` |
| T-021 | `tests/test_api.py::test_invalid_token_is_rejected` | `SUSTANCIAL` |
| T-022 | `tests/test_api.py::test_me_returns_authenticated_principal` | `SUSTANCIAL` |
| T-023 | `tests/test_api.py::test_owner_creates_case_as_authenticated_actor` | `SUSTANCIAL` |
| T-024 | `tests/test_api.py::test_spoofable_actor_fields_are_rejected` | `SUSTANCIAL` |
| T-025 | `tests/test_api.py::test_viewer_cannot_create_case` | `SUSTANCIAL` |
| T-026 | `tests/test_api.py::test_non_admin_cannot_create_case_for_another_organization` | `SUSTANCIAL` |
| T-027 | `tests/test_api.py::test_owner_lists_only_their_own_cases` | `SUSTANCIAL` |
| T-028 | `tests/test_api.py::test_cross_organization_case_access_is_denied` | `SUSTANCIAL` |
| T-029 | `tests/test_api.py::test_owner_can_submit_case_for_review_but_cannot_approve` | `SUSTANCIAL` |
| T-030 | `tests/test_api.py::test_reviewer_approves_and_advances_case` | `SUSTANCIAL` |
| T-031 | `tests/test_api.py::test_case_owner_cannot_activate_case` | `SUSTANCIAL` |
| T-032 | `tests/test_api.py::test_system_admin_can_list_cases_across_organizations` | `SUSTANCIAL` |
| T-033 | `tests/test_api_persistence.py::test_api_recovers_case_from_shared_sqlite_database` | `SUSTANCIAL` |
| T-034 | `tests/test_aria.py::test_pass_receipt_allows_governance_activation` | `SUSTANCIAL` |
| T-035 | `tests/test_aria.py::test_open_critical_finding_blocks_activation` | `SUSTANCIAL` |
| T-036 | `tests/test_aria.py::test_remediation_and_rerun_keep_history_and_can_pass` | `SUSTANCIAL` |
| T-037 | `tests/test_aria.py::test_critical_finding_cannot_be_closed_as_accepted_risk` | `SUSTANCIAL` |
| T-038 | `tests/test_aria.py::test_missing_required_family_prevents_receipt` | `SUSTANCIAL` |
| T-039 | `tests/test_aria.py::test_material_blueprint_change_invalidates_campaign` | `SUSTANCIAL` |
| T-040 | `tests/test_aria.py::test_failed_test_requires_a_finding` | `SUSTANCIAL` |
| T-041 | `tests/test_atlas.py::test_builds_traceable_briefing_with_four_scenarios` | `SUSTANCIAL` |
| T-042 | `tests/test_atlas.py::test_recording_briefing_does_not_activate_kernel_case` | `SUSTANCIAL` |
| T-043 | `tests/test_atlas.py::test_fingerprint_is_reproducible_for_same_payload` | `SUSTANCIAL` |
| T-044 | `tests/test_atlas.py::test_requires_exactly_one_scenario_of_each_type` | `SUSTANCIAL` |
| T-045 | `tests/test_atlas.py::test_rejects_source_more_sensitive_than_kernel_case` | `SUSTANCIAL` |
| T-046 | `tests/test_atlas.py::test_rejects_unknown_source_reference` | `SUSTANCIAL` |
| T-047 | `tests/test_atlas.py::test_source_confidence_must_be_valid_percentage` | `SUSTANCIAL` |
| T-048 | `tests/test_atlas_api.py::test_owner_builds_traceable_briefing_without_recording` | `SUSTANCIAL` |
| T-049 | `tests/test_atlas_api.py::test_same_input_produces_same_atlas_fingerprint` | `SUSTANCIAL` |
| T-050 | `tests/test_atlas_api.py::test_reviewer_records_briefing_and_proof_receipt` | `SUSTANCIAL` |
| T-051 | `tests/test_atlas_api.py::test_case_owner_cannot_record_final_briefing` | `SUSTANCIAL` |
| T-052 | `tests/test_atlas_api.py::test_org_admin_cannot_record_briefing_for_case_they_own` | `SUSTANCIAL` |
| T-053 | `tests/test_atlas_api.py::test_broken_source_reference_is_rejected` | `SUSTANCIAL` |
| T-054 | `tests/test_atlas_api.py::test_incomplete_scenario_set_is_rejected` | `SUSTANCIAL` |
| T-055 | `tests/test_atlas_api.py::test_source_sensitivity_cannot_exceed_case_sensitivity` | `SUSTANCIAL` |
| T-056 | `tests/test_atlas_api.py::test_duplicate_entity_ids_are_rejected` | `SUSTANCIAL` |
| T-057 | `tests/test_atlas_api.py::test_viewer_and_other_organization_cannot_build` | `SUSTANCIAL` |
| T-058 | `tests/test_atlas_api.py::test_recorded_briefing_survives_application_restart` | `SUSTANCIAL` |
| T-059 | `tests/test_auth.py::test_authenticator_matches_registered_token` | `SUSTANCIAL` |
| T-060 | `tests/test_auth.py::test_role_permission_matrix_is_least_privilege` | `SUSTANCIAL` |
| T-061 | `tests/test_auth.py::test_environment_loader_builds_principal` | `SUSTANCIAL` |
| T-062 | `tests/test_auth.py::test_invalid_environment_json_is_rejected` | `SUSTANCIAL` |
| T-063 | `tests/test_auth.py::test_empty_environment_produces_locked_api` | `SUSTANCIAL` |
| T-064 | `tests/test_kernel.py::test_case_requires_approval_before_approved_state` | `SUSTANCIAL` |
| T-065 | `tests/test_kernel.py::test_green_case_can_be_approved_and_activated` | `SUSTANCIAL` |
| T-066 | `tests/test_kernel.py::test_orange_case_requires_separate_approver` | `SUSTANCIAL` |
| T-067 | `tests/test_kernel.py::test_conditional_approval_requires_conditions` | `SUSTANCIAL` |
| T-068 | `tests/test_kernel.py::test_invalid_transition_is_rejected` | `SUSTANCIAL` |
| T-069 | `tests/test_kernel.py::test_repository_returns_defensive_copy` | `SUSTANCIAL` |
| T-070 | `tests/test_oaaa_api.py::test_health_declares_temporary_oaaa_control_plane_persistence` | `SUSTANCIAL` |
| T-071 | `tests/test_oaaa_api.py::test_owner_creates_draft_with_server_derived_identity_and_scope` | `SUSTANCIAL` |
| T-072 | `tests/test_oaaa_api.py::test_spoofable_identity_fields_are_rejected` | `SUSTANCIAL` |
| T-073 | `tests/test_oaaa_api.py::test_same_definition_produces_same_safety_fingerprint` | `SUSTANCIAL` |
| T-074 | `tests/test_oaaa_api.py::test_revision_detects_material_change_and_preserves_history` | `SUSTANCIAL` |
| T-075 | `tests/test_oaaa_api.py::test_unchanged_definition_is_marked_non_material` | `SUSTANCIAL` |
| T-076 | `tests/test_oaaa_api.py::test_owner_submits_draft_for_review_but_cannot_submit_twice` | `SUSTANCIAL` |
| T-077 | `tests/test_oaaa_api.py::test_viewer_and_auditor_are_read_only` | `SUSTANCIAL` |
| T-078 | `tests/test_oaaa_api.py::test_case_owner_cannot_design_for_another_owner_in_same_organization` | `SUSTANCIAL` |
| T-079 | `tests/test_oaaa_api.py::test_cross_organization_blueprint_access_is_denied` | `SUSTANCIAL` |
| T-080 | `tests/test_oaaa_api.py::test_missing_required_aria_family_is_rejected` | `SUSTANCIAL` |
| T-081 | `tests/test_oaaa_api.py::test_wildcard_tool_operation_is_rejected` | `SUSTANCIAL` |
| T-082 | `tests/test_oaaa_api.py::test_no_activation_endpoint_is_exposed` | `SUSTANCIAL` |
| T-083 | `tests/test_oaaa_blueprint.py::test_blueprint_starts_as_draft_and_is_versioned_in_vault` | `SUSTANCIAL` |
| T-084 | `tests/test_oaaa_blueprint.py::test_blueprint_rejects_wildcards_and_self_elevation_actions` | `SUSTANCIAL` |
| T-085 | `tests/test_oaaa_blueprint.py::test_activation_is_blocked_without_clearance_and_human_approval` | `SUSTANCIAL` |
| T-086 | `tests/test_oaaa_blueprint.py::test_stale_clearance_fingerprint_is_rejected` | `SUSTANCIAL` |
| T-087 | `tests/test_oaaa_blueprint.py::test_no_apto_clearance_blocks_the_blueprint` | `SUSTANCIAL` |
| T-088 | `tests/test_oaaa_blueprint.py::test_approved_blueprint_requires_aria_receipt_before_activation` | `SUSTANCIAL` |
| T-089 | `tests/test_oaaa_blueprint.py::test_happy_path_records_vault_and_aria_links_without_runtime_deployment` | `SUSTANCIAL` |
| T-090 | `tests/test_oaaa_blueprint.py::test_orange_blueprint_requires_owner_approver_separation` | `SUSTANCIAL` |
| T-091 | `tests/test_oaaa_blueprint.py::test_material_revision_invalidates_clearance_and_approval` | `SUSTANCIAL` |
| T-092 | `tests/test_oaaa_blueprint.py::test_safety_fingerprint_does_not_change_during_governance_transition` | `SUSTANCIAL` |
| T-093 | `tests/test_output_vault.py::test_append_only_lifecycle_creates_receipt_and_kernel_records` | `SUSTANCIAL` |
| T-094 | `tests/test_output_vault.py::test_approval_requires_tests_and_evidence` | `SUSTANCIAL` |
| T-095 | `tests/test_output_vault.py::test_orange_artifact_requires_separate_evaluator` | `SUSTANCIAL` |
| T-096 | `tests/test_output_vault.py::test_integrity_hash_is_reproducible_for_same_substantive_payload` | `SUSTANCIAL` |
| T-097 | `tests/test_output_vault.py::test_json_and_markdown_exports_include_traceability` | `SUSTANCIAL` |
| T-098 | `tests/test_output_vault.py::test_only_approved_artifacts_can_be_superseded` | `SUSTANCIAL` |
| T-099 | `tests/test_sqlalchemy_repository.py::test_sqlalchemy_repository_satisfies_kernel_contract` | `TRIVIAL` |
| T-100 | `tests/test_sqlalchemy_repository.py::test_case_and_events_survive_repository_restart` | `SUSTANCIAL` |
| T-101 | `tests/test_sqlalchemy_repository.py::test_resaving_case_does_not_duplicate_events` | `SUSTANCIAL` |
| T-102 | `tests/test_sqlalchemy_repository.py::test_append_only_collections_are_reconstructed` | `SUSTANCIAL` |
| T-103 | `tests/test_sqlalchemy_repository.py::test_append_methods_are_idempotent_by_record_id` | `SUSTANCIAL` |
| T-104 | `tests/test_sqlalchemy_repository.py::test_list_cases_returns_all_persisted_cases` | `SUSTANCIAL` |
| T-105 | `tests/test_sqlalchemy_repository.py::test_missing_case_raises_domain_error` | `SUSTANCIAL` |
| T-106 | `tests/test_vigilance.py::test_grant_starts_as_draft_and_uses_explicit_actions` | `SUSTANCIAL` |
| T-107 | `tests/test_vigilance.py::test_sensitive_action_requires_named_human_approval` | `SUSTANCIAL` |
| T-108 | `tests/test_vigilance.py::test_read_is_allowed_but_delete_and_out_of_scope_resources_are_denied` | `SUSTANCIAL` |
| T-109 | `tests/test_vigilance.py::test_agent_cannot_issue_or_approve_its_own_permissions` | `SUSTANCIAL` |
| T-110 | `tests/test_vigilance.py::test_emergency_disable_blocks_all_actions_and_preserves_history` | `SUSTANCIAL` |
| T-111 | `tests/test_vigilance.py::test_revision_invalidates_old_action_approval` | `SUSTANCIAL` |
| T-112 | `tests/test_vigilance.py::test_orange_grant_requires_owner_approver_separation` | `SUSTANCIAL` |
| T-113 | `tests/test_vigilance.py::test_execution_record_requires_allowed_authorization` | `SUSTANCIAL` |

| T-114 | `tests/test_output_vault.py::test_create_draft_rejects_owner_mismatch_without_residual_records` | `SUSTANCIAL` |

### Huecos de cobertura detectados

Un hueco significa que no existe un test específico suficiente o que al menos una rama material de la lógica no fue ejecutada en la medición. No implica automáticamente que el código falle; implica que una regresión podría entrar sin ser detectada.

#### P0 · Antes de ampliar superficie o autonomía

1. **OAAA · gates de activación completos.** Añadir pruebas separadas para decisión Aegis no desplegable, gates incompletos, nota vacía, evidencia de aprobación ausente, aprobación rechazada y fingerprint de aprobación obsoleto.
2. **OAAA · validación exhaustiva del ARIA Receipt.** Probar receipt de otro blueprint, fingerprint obsoleto, críticos abiertos, verdict bloqueante, hash inválido e identificador ausente.
3. **OAAA · suspensión.** Probar `ACTIVE → SUSPENDED`, intento desde cualquier otro estado, motivo vacío, historia append-only y evidencia generada.
4. **Vigilance · matriz completa de autorización.** Probar sujeto incorrecto, grant no activo, expirado, revisión vencida, acción denegada o no permitida, recurso vacío o fuera de scope, aprobación ausente, pendiente, denegada y aprobada.
5. **Vigilance · ciclo de aprobación y revocación.** Probar request sobre grant no activo, requester incorrecto, acción que no requiere aprobación, request obsoleto, fingerprint cambiado, autoaprobación, decisión duplicada o expirada, rationale vacío, `revoke_grant` y ejecución asociada a versión obsoleta.
6. **ARIA · independencia y finalización.** Probar separación owner/finalizer en ORANGE y RED, decidir si executor/finalizer debe ser también una separación obligatoria, familia fuera del plan, segunda resolución, caso del blueprint cambiado y verdict `PASS_WITH_REMEDIATION`.
7. **Output Vault · autorización de identidad.** `RESUELTO EN VERIFICATION.md v2.1`. `create_draft` comprueba que `owner_id` coincide con el owner del caso Kernel antes de cualquier persistencia. La prueba de regresión verifica el rechazo y la ausencia de versiones, outputs y evidencias residuales.
8. **Output Vault · decisiones.** Separar las pruebas de evidencia ausente y test reference ausente; añadir rechazo, rationale vacío, decisión fuera de `REVIEW`, revisión de lineage superseded y motivo de supersession vacío.
9. **Persistencia del control plane.** OAAA, ARIA, Vigilance y Output Vault continúan con repositorios in-memory. No existen pruebas de reinicio, transacción o integridad durable para su estado operativo.
10. **PostgreSQL/Supabase.** No hay prueba real de PostgreSQL, migraciones, RLS, backups, rollback, concurrencia, locking ni recuperación. SQLite no cierra este riesgo.

#### P1 · Endurecimiento del Bloque 0

1. **Repositorios append-only.** Cubrir duplicados, IDs inexistentes, versiones saltadas, parent incorrecto, receipt duplicado, defensividad de copias y orden estable en los repositorios OAAA, ARIA, Vigilance y Output Vault.
2. **Kernel.** Probar título vacío, rationale vacío, decisión negativa bloqueando transición, todas las rutas `SUSPENDED` y `CLOSED`, aprobación duplicada y razones de transición vacías.
3. **Aegis.** Añadir tests parametrizados en los límites exactos de cada umbral de decisión y dimensión, campos de texto vacíos, blocker vacío y traducción API de caso inexistente y errores de dominio.
4. **Atlas.** Cubrir strings obligatorios vacíos, probabilidades y confianza no enteras, horizonte inválido, URI vacía, colecciones obligatorias vacías, severidades restantes, mismatch de caso/organización y 404 en API.
5. **Modelos OAAA, ARIA, Vigilance y Vault.** Ejecutar todas las validaciones de invariants: valores vacíos, duplicados, tiempos invertidos, acciones incompatibles, wildcards, versiones inválidas, hashes y combinaciones de estado incoherentes.
6. **Autenticación y configuración.** Probar JSON válido que no sea lista, registro que no sea objeto, claves/UUID/rol inválidos, token vacío, todos los valores booleanos de entorno y valor booleano inválido.
7. **Container y selección de repositorio.** Cubrir repositorio inyectado, fallback in-memory, URL por argumento y entorno, auto-create verdadero/falso y dialecto PostgreSQL.
8. **Contratos HTTP.** Añadir 404/409/422 para IDs desconocidos y transiciones inválidas en todos los endpoints, JSON malformado, content type incorrecto, UUID inválido y prevención de fuga de detalles internos.
9. **Contrato OpenAPI.** Congelar y comparar el esquema público esperado para detectar exposición accidental de endpoints, campos spoofeables o cambios incompatibles.
10. **Tiempo.** Usar un reloj inyectable y probar igualdad exacta al vencimiento, justo antes/después, timezone y clock skew en Vigilance y futuras expiraciones de Clearance.

#### P2 · Calidad avanzada de la suite

1. Introducir tests property-based para fingerprints, serialización, secuencias de estado y combinaciones de permisos.
2. Ejecutar mutation testing para comprobar que las aserciones matan cambios en umbrales, comparadores, controles de identidad y gates.
3. Añadir fuzzing de schemas, payloads y parsers, con límites de tamaño definidos.
4. Añadir pruebas de concurrencia, idempotencia bajo repetición y cargas simultáneas.
5. Integrar análisis SAST/dependencias/secretos como evidencia complementaria; no sustituye ARIA ni las pruebas de comportamiento.
6. Establecer gates separados de statements, branches y mutación. Un único porcentaje agregado puede ocultar ramas críticas.

### Módulos con menor cobertura combinada

| Módulo | Cobertura |
|---|---:|
| `dataforge/repository.py` | 66,7 % |
| `api/container.py` | 68,5 % |
| `oaaa/service.py` | 72,1 % |
| `vigilance/service.py` | 74,7 % |
| `vigilance/repository.py` | 77,0 % |
| `api/aegis_routes.py` | 78,3 % |
| `dataforge/service.py` | 79,3 % |
| `aria/repository.py` | 79,4 % |
| `api/app.py` | 80,8 % |

Estos porcentajes orientan la prioridad, pero no miden por sí solos la importancia del riesgo. Una sola rama sin probar en un gate de autorización puede ser más crítica que decenas de líneas auxiliares cubiertas.

### Capacidades no construidas que no deben confundirse con cobertura

No se consideran “cubiertas” ni “fallidas” por la suite actual:

- runtime productivo de agentes;
- credenciales, herramientas o ejecuciones externas reales;
- API ARIA v0.7 y API avanzada Vigilance;
- persistencia completa del control plane;
- PostgreSQL/Supabase productivo, migraciones, RLS y backups;
- telemetría continua de trayectorias y correlación multiagente;
- infraestructura o hardware neuromórfico;
- constitución, contratación, pagos o asignación autónoma de capital por Venture Foundry.

Son capacidades pendientes o arquitectura objetivo. Crear tests simulados no autorizaría presentarlas como construidas.

## 12. Auditoría de gaps entre issues, Pull Requests y commits · VERIFICATION.md v2.2

### Objetivo y método

- Fecha de revisión: `2026-07-29`.
- Referencias auditadas: `#15`, `#18`, `#19`, `#21`, `#23`, `#25`, `#26`, `#28` y `#30`.
- Total revisado: `9/9`.
- Método: identificar el tipo real de cada referencia, comprobar su estado de cierre, localizar el Pull Request de implementación cuando correspondía, registrar el merge commit y verificar la continuidad hasta `main`.
- Estado de `main` tomado como referencia: `1c6713c2c64f5ac315ecbc1ae53b8840ceecc9eb`.
- Resultado global: `FUNCIONA VERIFICADO · TRAZABILIDAD DOCUMENTAL 9/9 · SIN TRABAJO PERDIDO DETECTADO`.

GitHub comparte una única secuencia numérica entre issues y Pull Requests. Por ello, varios números que parecían Pull Requests cerrados sin fusionar eran en realidad issues de implementación cuyo Pull Request ocupaba el número siguiente.

### Matriz de disposición

| Referencia | Tipo real | Disposición | Trazabilidad | Clasificación |
|---|---|---|---|---|
| `#15` | Issue | Placeholder creado accidentalmente y cerrado como `not_planned`. No tenía trabajo asociado. | Sin commit ni PR requerido. | `DESCARTADO DELIBERADAMENTE · SIN PÉRDIDA` |
| `#18` | Issue | Precursor parcialmente duplicado, cerrado como supersedido. | Núcleo cubierto por `#19` y PR `#20`, merge `685499ee7abc6c01128477c0a2f6ef90bde73d3b`. Residuos trasladados a `#46`. | `SUPERSEDIDO · RESIDUO TRAZADO · SIN PÉRDIDA` |
| `#19` | Issue | P8 completado. | PR `#20`, merge `685499ee7abc6c01128477c0a2f6ef90bde73d3b`. | `COMPLETADO Y FUSIONADO` |
| `#21` | Issue | P9 completado. | PR `#22`, merge `d059088b007cce62f91f4e81b574b6d831986c7b`. | `COMPLETADO Y FUSIONADO` |
| `#23` | Issue | P10 completado. | PR `#24`, merge `a6d856cc43877bd3d26063ebd59c62e41ac32d2e`. | `COMPLETADO Y FUSIONADO` |
| `#25` | Pull Request | Actualización documental sin cambios funcionales. | Fusionado mediante `184e6d5e84c045801768e7c54894c7e1935b4145`. | `PR DOCUMENTAL FUSIONADO` |
| `#26` | Issue | P11 completado. | PR `#27`, merge `e80c01008cd616ba5e850c4396631f10fd418c16`. | `COMPLETADO Y FUSIONADO` |
| `#28` | Issue | P12 completado. | PR `#29`, merge `f4bf8777e8eeab42578166a38a153ac0dcccfd52`. | `COMPLETADO Y FUSIONADO` |
| `#30` | Issue | P13 completado. | PR `#31`, merge `3feb2306ce4bca08d866fe98e7011505ff07467b`. | `COMPLETADO Y FUSIONADO` |

### Continuidad en `main`

El merge de PR `#31`, commit `3feb2306ce4bca08d866fe98e7011505ff07467b`, es ancestro del `main` de referencia. La comparación entre ambos commits mostró:

- `main` por delante: `31` commits;
- `main` por detrás: `0` commits;
- merge base: `3feb2306ce4bca08d866fe98e7011505ff07467b`.

Las relaciones de base y merge de los PR `#20`, `#22`, `#24`, `#27`, `#29` y `#31` forman una cadena incorporada progresivamente a `main`. El PR `#25` también consta como fusionado entre P10 y P11.

### Dictamen

- Pull Requests auditados cerrados sin fusionar: `0`.
- Referencias descartadas deliberadamente: `1`, issue `#15`.
- Referencias supersedidas con residuos trazados: `1`, issue `#18`.
- Issues completados mediante Pull Request fusionado: `6`.
- Pull Requests documentales fusionados: `1`, PR `#25`.
- Trabajo perdido detectado: `0`.
- Trabajo residual no perdido: hardening de `#18` trasladado explícitamente a `#46`.

La auditoría cierra el gap documental. No demuestra por sí sola que todas las capacidades estén listas para piloto o producción; únicamente confirma la disposición y continuidad del trabajo asociado a las nueve referencias revisadas.

## 13. Conclusión

La reproducibilidad documental del README, los 16 endpoints automáticos, los 22 controles negativos y los 20 controles de persistencia quedan como `FUNCIONA VERIFICADO`.

Los primeros ocho endpoints también quedan como `FUNCIONA VERIFICADO · OBSERVACIÓN HUMANA NOMINAL` en Swagger. La suite queda clasificada como `112/114 SUSTANCIALES` y `2/114 TRIVIALES`; esta proporción favorable no equivale a cobertura completa.

La auditoría de referencias `#15`, `#18`, `#19`, `#21`, `#23`, `#25`, `#26`, `#28` y `#30` queda cerrada como `9/9`, sin Pull Requests cerrados sin fusionar ni trabajo perdido detectado.

Esto no demuestra todavía identidad productiva, PostgreSQL/Supabase, cobertura completa de ramas, concurrencia productiva, runtime de agentes, integraciones reales, cumplimiento ni certificación. La persistencia operativa OAAA sobre SQLite queda verificada posteriormente en la Sesión 4-5.

## Persistencia operativa OAAA sobre SQLite · Sesión 4-5

**Estado:** `FUNCIONA VERIFICADO · ENTORNO LOCAL CONTROLADO`

Se ha migrado el control plane operativo de OAAA desde repositorios exclusivamente
en memoria hacia persistencia SQLAlchemy sobre SQLite, conservando fallback
`in-memory-development` cuando no existe una URL de base de datos configurada.

### Capacidades verificadas

- `SQLAlchemyAgentBlueprintRepository` conserva blueprints, versiones,
  aprobaciones humanas y activation receipts.
- `SQLAlchemyOutputVaultRepository` conserva versiones de artefactos y
  Proof Receipts.
- `ApplicationContainer` selecciona persistencia SQLAlchemy para Kernel,
  OAAA y Output Vault cuando se configura `ASTRYNN_DATABASE_URL`.
- La aplicación puede reconstruirse usando la misma base SQLite sin perder
  el blueprint ni su historial.
- El workflow continúa después del reinicio:
  `crear DRAFT → reiniciar → recuperar → revisar → enviar a IN_REVIEW`.
- Se conservan el mismo `blueprint_id`, el fingerprint de seguridad y la
  relación correcta entre versiones padre e hijas.

### Evidencia local

- Suite completa: `122 passed`.
- Calidad estática: `ruff check .` → `All checks passed!`.
- Test de continuidad HTTP:
  `test_oaaa_http_workflow_continues_after_sqlite_restart`.
- Tests de repositorio:
  `test_sqlalchemy_oaaa_repository.py`.
- Tests de Output Vault:
  `test_sqlalchemy_output_vault_repository.py`.
- Tests de selección del contenedor:
  `test_container_uses_sqlite_for_oaaa_control_plane` y
  `test_container_uses_sqlite_for_output_vault`.

### Límites expresos

Este resultado **no equivale** a `PILOT READY` ni a `PRODUCTION READY`.

No demuestra todavía:

- PostgreSQL o Supabase productivo;
- RLS y aislamiento multi-tenant en base de datos;
- migraciones productivas versionadas;
- estrategia de backup, restore y disaster recovery;
- concurrencia productiva;
- identidad y autenticación productivas;
- exposición pública o despliegue en VPS;
- agentes runtime;
- integraciones con sistemas reales;
- uso de datos reales de clientes;
- cumplimiento regulatorio o certificación.

### Custodia de evidencia remota

La evidencia local y remota queda validada para el alcance SQLite descrito.

- Pull Request: `#50`.
- Commit de evidencia funcional:
  `ff0333aebc3a10188e33b15f83ecd86a407472eb`.
- Suite local: `122 passed`.
- Ruff local: `All checks passed!`.
- CI: Run ID `30950513728` · `SUCCESS`.
- Restart Persistence Verification:
  Run ID `30950513711` · `SUCCESS`.
- Human Verification:
  Run ID `30950513679` · `SUCCESS`.
- README Clean-room Verification:
  Run ID `30950513687` · `SUCCESS`.
- Remaining Endpoint Verification:
  Run ID `30950513675` · `SUCCESS`.
- Deliberate Negative Verification:
  Run ID `30950513705` · `SUCCESS`.

La verificación remota confirma que dos procesos Uvicorn distintos pueden usar
la misma base SQLite y recuperar el estado persistente de Kernel, OAAA y Output
Vault después del reinicio.

Esta custodia no amplía el alcance a PostgreSQL, Supabase, RLS, concurrencia
productiva, backups, identidad productiva, `PILOT READY` ni `PRODUCTION READY`.


## Persistencia operativa sobre PostgreSQL · Sesión 6 / P16B

**Estado:** `FUNCIONA VERIFICADO · ENTORNO LOCAL CONTROLADO + CI PRINCIPAL REMOTO`

Se ha validado la persistencia operativa de Kernel, OAAA y Output Vault sobre
PostgreSQL real mediante la implementación SQLAlchemy existente, sin introducir
una implementación paralela específica de proveedor.

El backend se identifica como:

`sqlalchemy-postgresql`

### Capacidades verificadas

- Kernel, OAAA y Output Vault utilizan PostgreSQL mediante la misma
  `ASTRYNN_DATABASE_URL`.
- El flujo HTTP persiste después de reconstruir completamente la aplicación:
  `crear → persistir → reconstruir → recuperar → revisar → enviar a IN_REVIEW`.
- Se recuperan el mismo blueprint, owner y safety fingerprint.
- Se preservan versiones y `parent_version_id`.
- Se rechazan versiones OAAA duplicadas.
- Se rechazan versiones OAAA saltadas.
- Se rechaza un `parent_version_id` incoherente.
- Persisten Human Approval Records.
- Persisten Activation Receipts.
- Persisten Output Vault artifacts.
- Persisten Output Vault Proof Receipts.
- Se rechazan versiones duplicadas de Output Vault.
- El aislamiento cross-organization continúa rechazando acceso de otra
  organización.
- Un rechazo por `owner_id` inválido en Output Vault no deja artefactos,
  outputs ni evidencia residual.

### Evidencia local

PostgreSQL utilizado:

- `postgres:16-alpine`
- contenedor efímero local;
- datos sintéticos;
- puerto local `127.0.0.1:55432`;
- sin datos reales de clientes.

Resultados:

- Gate PostgreSQL específico: `3 passed in 4.64s`.
- Suite completa con PostgreSQL disponible: `125 passed in 3.84s`.
- `ruff check .` → `All checks passed!`.
- `git diff --check` → limpio.

Tests PostgreSQL:

- `test_postgresql_oaaa_workflow_survives_restart`
- `test_postgresql_repository_contracts_survive_restart`
- `test_postgresql_cross_org_isolation_and_atomic_vault_rejection`

### Commits funcionales

- `72b1863` · `test: verify PostgreSQL persistence in CI`
- `791439d` · `test: strengthen PostgreSQL persistence contracts`

Pull Request:

- `#53`

### Custodia de evidencia remota

Sobre commit `bb4b5d2c20aac3a9359bbdcdd65ab76a7ef4f44f`:

- CI:
  Run ID `31320064970` · `SUCCESS`.
- Restart Persistence Verification:
  Run ID `31320064953` · `SUCCESS`.
- Human Verification:
  Run ID `31320064933` · `SUCCESS`.
- README Clean-room Verification:
  Run ID `31320064930` · `SUCCESS`.
- Remaining Endpoint Verification:
  Run ID `31320064934` · `SUCCESS`.
- Deliberate Negative Verification:
  Run ID `31320064935` · `SUCCESS`.

Los seis gates remotos requeridos finalizaron correctamente sobre el mismo
commit de evidencia documental y funcional.

Esta custodia confirma el alcance PostgreSQL descrito en esta sección y no
amplía los límites expresos a Supabase, RLS productivo, backups, alta
disponibilidad, runtime, PILOT READY ni PRODUCTION READY.

### Límites expresos

Este resultado NO demuestra todavía:

- Supabase administrado;
- Supabase Auth;
- RLS productivo;
- aislamiento multi-tenant garantizado por políticas de base de datos;
- migraciones productivas versionadas;
- concurrencia productiva;
- locking productivo;
- backup/restore/disaster recovery;
- alta disponibilidad;
- identidad productiva;
- datos reales de clientes;
- despliegue público;
- VPS;
- agentes runtime;
- integraciones reales;
- `PILOT READY`;
- `PRODUCTION READY`;
- cumplimiento regulatorio o certificación.

La validación PostgreSQL no amplía automáticamente ninguno de esos claims.

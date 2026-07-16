# VERIFICATION.md · Bloque 0 · Verificación humana del prototipo

Fecha de apertura: 2026-07-16

Repositorio: `Sellynet/astrynn-devforge-gpt`

Estado global: `BLOQUE 0 PARCIALMENTE COMPLETADO · 16/16 ENDPOINTS VERIFICADOS`

## 1. Regla de evidencia

Estados permitidos:

- `FUNCIONA VERIFICADO`: ejecución reproducible completada y evidencia revisada.
- `FALLA`: el comportamiento observado contradice el resultado esperado.
- `DUDOSO`: evidencia incompleta, ambigua o capacidad no construida.
- `PENDIENTE`: prueba todavía no ejecutada.

Una CI verde no cierra por sí sola todo el Bloque 0. Siguen pendientes las pruebas negativas, persistencia tras reinicio, PostgreSQL/Supabase, lectura humana de tests y revisión de gaps de Pull Requests.

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
- PR head: `a0b1d9056f1bed80879e03fccd5c9eeb4f57df17`
- Python: `3.11.15`
- Ruff: `All checks passed!`
- pytest: `113 passed, 1 warning`
- Resultado: `8/8 FUNCIONA VERIFICADO`
- Artifact: `block0-remaining-endpoints-1`
- Artifact SHA-256: `7854959c7233498d78036777383a18a9beb2d84aace726d20d2f778496314bd7`

Informe permanente:

`docs/verification/BLOCK0_REMAINING_8_ENDPOINTS_2026-07-16.md`

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

## 4. Evidencia funcional confirmada

### Kernel y autorización

- identidad derivada del token;
- creación, listado y lectura del caso;
- transición `DRAFT → IN_REVIEW`;
- aprobación independiente con owner y reviewer separados.

### Aegis

- evaluación determinista con decisión `APTO`;
- puntuación total `9`;
- fingerprint de entrada;
- registro de Clearance Report;
- `output_id` y `evidence_id`;
- estado del artefacto `REVIEW`;
- sin aprobación, activación o despliegue como efecto secundario.

### Atlas

- FACT, INFERENCE, ASSUMPTION y RECOMMENDATION tipadas;
- fuentes y fingerprints trazables;
- resumen ejecutivo;
- registro de briefing con output y evidencia;
- declaración explícita de apoyo a decisión, sin control de infraestructura.

### OAAA

- blueprint v1 en `DRAFT`;
- identidad y organización derivadas del caso;
- safety fingerprint e integrity hash;
- lectura e historial;
- revisión material a v2 con parent version;
- envío a `IN_REVIEW` en v3;
- sin endpoint ni efecto de activación.

## 5. Límites y hallazgos abiertos

### README

Estado: `FALLA · DOCUMENTACIÓN INSUFICIENTE`

El README permite instalar y ejecutar Ruff/pytest, pero no documenta todavía el recorrido completo desde clone hasta API operativa, tokens, Uvicorn, SQLite, Swagger, reinicio y persistencia.

### OAAA

Estado: `DUDOSO · CAPACIDAD PRODUCTIVA NO CONSTRUIDA`

El control plane declara:

`in-memory-development`

Los endpoints y el versionado funcionan dentro del proceso activo, pero no se ha demostrado supervivencia tras reinicio.

### Warning de dependencias

Estado: `DUDOSO · DEUDA TÉCNICA NO BLOQUEANTE`

pytest registra un `StarletteDeprecationWarning` relacionado con `httpx` y `starlette.testclient`.

## 6. Pendientes para cerrar el Bloque 0

1. Corregir el README y repetir el levantamiento siguiendo solo esa documentación.
2. Ejecutar pruebas negativas deliberadas:
   - token ausente e inválido;
   - acceso cross-organization;
   - autoaprobación;
   - owner registrando Clearance o Atlas final;
   - transición inválida;
   - score fuera de rango;
   - blocker crítico y specialist trigger;
   - wildcard de tools;
   - familia ARIA ausente;
   - acceso OAAA de otro owner;
   - envío duplicado;
   - intento de activación.
3. Verificar persistencia Kernel SQLite después de reiniciar Uvicorn.
4. Documentar la pérdida esperada de OAAA tras reinicio.
5. Construir persistencia OAAA antes de verificar restart.
6. Repetir persistencia Kernel con PostgreSQL/Supabase.
7. Leer manualmente los tests y valorar su calidad.
8. Revisar gaps entre Pull Requests y commits.
9. Resolver o aceptar formalmente el warning.
10. Obtener revisión humana nominal.

## 7. Conclusión

Los 16 endpoints de la API privada v0.6.0 quedan como `FUNCIONA VERIFICADO` dentro de ejecuciones reproducibles de GitHub Actions.

Esto no demuestra todavía resistencia adversarial, persistencia completa, identidad productiva, runtime de agentes, integraciones reales, cumplimiento ni certificación.

El siguiente tramo obligatorio son las pruebas negativas deliberadas.

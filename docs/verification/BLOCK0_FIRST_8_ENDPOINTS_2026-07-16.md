# Block 0 · Evidencia de los primeros 8 endpoints

Fecha: 2026-07-16

Repositorio: `Sellynet/astrynn-devforge-gpt`

Workflow: `Block 0 Human Verification`

Run válido: `29487356386` · número `2`

Commit evaluado: `4bf36d85f378b01e13ef7209361fd50aa8e5960f`

## 1. Entorno

- Ubuntu 24.04
- Python 3.11.15
- pip 26.1.2
- instalación editable mediante `pip install -e . ruff pytest`
- API levantada con Uvicorn en `127.0.0.1:8000`
- persistencia de verificación: SQLite sintético
- autenticación: Bearer RBAC de desarrollo
- identidades sintéticas separadas para owner y reviewer

## 2. Calidad

| Control | Resultado |
|---|---|
| Ruff | `All checks passed!` |
| pytest | `113 passed, 1 warning in 2.55s` |
| API startup | correcto |
| Primeros 8 endpoints | `8/8 FUNCIONA VERIFICADO` |

Warning pendiente:

`StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.`

El warning no bloqueó la suite, pero debe revisarse antes de actualizar dependencias o declarar compatibilidad futura.

## 3. Resultado por endpoint

| ID | Método y ruta | Esperado | Observado | Clasificación |
|---|---|---:|---:|---|
| E-001 | `GET /health` | 200 | 200 | `FUNCIONA VERIFICADO` |
| E-002 | `GET /api/v1/me` | 200 | 200 | `FUNCIONA VERIFICADO` |
| E-003 | `POST /api/v1/cases` | 201 | 201 | `FUNCIONA VERIFICADO` |
| E-004 | `GET /api/v1/cases` | 200 | 200 | `FUNCIONA VERIFICADO` |
| E-005 | `GET /api/v1/cases/{case_id}` | 200 | 200 | `FUNCIONA VERIFICADO` |
| E-006 | `POST /api/v1/cases/{case_id}/transition` | 200 | 200 | `FUNCIONA VERIFICADO` |
| E-007 | `POST /api/v1/cases/{case_id}/approvals` | 201 | 201 | `FUNCIONA VERIFICADO` |
| E-008 | `POST /api/v1/aegis/cases/{case_id}/clearance/evaluate` | 200 | 200 | `FUNCIONA VERIFICADO` |

## 4. Evidencia observada

### E-001 · Health

```json
{
  "status": "ok",
  "service": "astrynn-devforge",
  "version": "0.6.0",
  "persistence": "sqlalchemy-sqlite",
  "authentication": "bearer-rbac-development",
  "oaaa_control_plane_persistence": "in-memory-development"
}
```

### E-002 · Principal autenticado

```json
{
  "actor_id": "22222222-2222-4222-8222-222222222222",
  "organization_id": "11111111-1111-4111-8111-111111111111",
  "role": "CASE_OWNER",
  "display_name": "Actions Owner"
}
```

### E-003 · Caso creado

Se observó:

- owner derivado del token;
- organización correcta;
- sensibilidad `ORANGE`;
- estado inicial `DRAFT`;
- evento `CASE_CREATED`.

Case ID de la ejecución válida:

`77c003c4-1737-4d24-893f-4140c1c83c04`

### E-004 · Listado

El listado del owner contenía el caso creado y no mostró casos de otros owners dentro del escenario sintético.

### E-005 · Lectura

La lectura devolvió el mismo ID, owner, organización, sensibilidad y evento de creación.

### E-006 · Transición

Se observó:

```text
DRAFT → IN_REVIEW
```

El evento `STATUS_CHANGED` conservó actor, estados y reason.

### E-007 · Aprobación

Se observó:

- reviewer distinto del owner;
- decisión `APPROVE_WITH_CONDITIONS`;
- condición `Human approval before any external action`;
- respuesta HTTP 201.

### E-008 · Aegis Clearance

Resultado:

```json
{
  "decision": "APTO",
  "total_score": 9,
  "methodology_version": "AEGIS-CLEARANCE-0.1",
  "input_fingerprint": "db8b58952920e0f3a858680796805bd3d98e096eadf609b2bab54b1eb0af02e4"
}
```

Controles observados:

- las nueve dimensiones tenían puntuación 1;
- no había triggers especializados;
- no había blockers críticos;
- se generó Proof Receipt;
- el caso permaneció en `IN_REVIEW`;
- la evaluación no aprobó, activó ni desplegó el caso.

## 5. Incidente del harness R-001

La primera ejecución, Run ID `29487147734`, mostró `111 passed, 2 failed` porque el workflow aplicó `ASTRYNN_DATABASE_URL` a toda la suite pytest. Eso provocó que pruebas independientes compartieran un archivo SQLite y acumularan registros.

La corrección consistió en:

1. ejecutar pytest sin variables de persistencia externas;
2. aplicar SQLite únicamente al proceso Uvicorn utilizado por la prueba de endpoints;
3. repetir la ejecución completa.

La ejecución R-002 terminó con `113 passed`.

Clasificación: `FALLA DEL HARNESS · CORREGIDA`.

## 6. Artefacto

Nombre:

`block0-human-verification-2`

Artifact ID:

`8370940305`

Digest:

`sha256:4ed3836f406b6567cb775c0f30df54e3cc492f327f9757ec293d1cf9f60749ef`

Contenido:

- entorno;
- instalación;
- Ruff;
- pytest;
- Uvicorn;
- consola de endpoints;
- resultados JSON;
- informe Markdown;
- resumen de Actions.

Retención configurada: 30 días.

## 7. Límite de esta evidencia

Esta ejecución confirma el comportamiento positivo de los primeros ocho endpoints en un entorno limpio y reproducible con SQLite.

No confirma todavía:

- todos los fallos deliberados;
- persistencia tras reinicio;
- PostgreSQL/Supabase;
- seguridad de producción;
- identidad productiva;
- runtime de agentes;
- acciones externas;
- cumplimiento o certificación regulatoria.

# VERIFICATION.md · Bloque 0 · Verificación humana del prototipo

Fecha de apertura: 2026-07-16

Repositorio: `Sellynet/astrynn-devforge-gpt`

Rama de trabajo: `verification/block-0-readme-and-first-8-endpoints`

Estado global: `EN CURSO · NO VERIFICADO TODAVÍA`

## 1. Propósito

Este archivo registra evidencia humana observable del Bloque 0. Una CI verde, un test automatizado o una afirmación documental no se marcan por sí solos como `FUNCIONA VERIFICADO`.

Estados permitidos:

- `FUNCIONA VERIFICADO`: una persona ejecutó la prueba, observó el resultado esperado y dejó evidencia suficiente.
- `FALLA`: el comportamiento observado contradice el resultado esperado o impide continuar.
- `DUDOSO`: hay evidencia incompleta, ambigua o no reproducida por una persona.
- `PENDIENTE`: prueba todavía no ejecutada.

No se utilizarán datos reales, secretos ni credenciales de clientes.

## 2. Paso 1 · Clonado y arranque siguiendo solo el README

### 2.1 Resultado provisional

Estado: `FALLA · DOCUMENTACIÓN INSUFICIENTE`

El README sí documenta:

```bash
python -m pip install --upgrade pip
pip install -e . ruff pytest
ruff check .
pytest -q
```

Pero no documenta:

1. comando de clonado y directorio de trabajo;
2. creación y activación de un entorno virtual;
3. comprobación explícita de Python 3.11 o superior;
4. comando para arrancar Uvicorn;
5. formato y ejemplos de `ASTRYNN_API_TOKENS_JSON`;
6. configuración opcional de `ASTRYNN_DATABASE_URL`;
7. comportamiento de `ASTRYNN_AUTO_CREATE_SCHEMA`;
8. URL de Swagger y procedimiento de prueba;
9. dos identidades separadas para owner y reviewer;
10. procedimiento de cierre y reinicio.

Además, el README indica todavía `Fase actual: fundación técnica y Kernel mínimo`, mientras el paquete y la API declaran versión `0.6.0`.

### 2.2 Fricciones observadas

| ID | Fricción | Clasificación | Estado |
|---|---|---|---|
| F-001 | El entorno de asistencia no pudo resolver GitHub por DNS al intentar clonar. | Entorno de verificación, no defecto probado del proyecto | `DUDOSO` |
| F-002 | El README no contiene un recorrido reproducible desde clone hasta API arrancada. | Documentación del proyecto | `FALLA` |
| F-003 | El README no explica tokens Bearer ni separación owner/reviewer. | Documentación del proyecto | `FALLA` |
| F-004 | El README no explica persistencia o creación de esquema. | Documentación del proyecto | `FALLA` |
| F-005 | El estado del README está desactualizado respecto a la API 0.6.0. | Documentación del proyecto | `FALLA` |

Conclusión del paso 1: una persona nueva no puede levantar y probar la API siguiendo únicamente el README. Esto debe corregirse antes de cerrar el Bloque 0.

## 3. Runbook suplementario para ejecutar desde móvil con GitHub Codespaces

Este runbook permite continuar la comprobación después de registrar el fallo documental del README. No borra el hallazgo anterior.

### 3.1 Crear el entorno

Desde el repositorio en GitHub:

1. Abrir `Code`.
2. Abrir `Codespaces`.
3. Crear un codespace sobre `main` o sobre esta rama de verificación.
4. Abrir el terminal.

Ejecutar:

```bash
python --version
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e . ruff pytest
ruff check .
pytest -q
```

Registrar aquí:

- versión de Python: `PENDIENTE`
- instalación editable: `PENDIENTE`
- Ruff: `PENDIENTE`
- pytest: `PENDIENTE`
- número de tests ejecutados: `PENDIENTE`
- duración: `PENDIENTE`
- mensajes o warnings: `PENDIENTE`

### 3.2 Configurar identidades sintéticas y SQLite

```bash
export ORG_ID='11111111-1111-4111-8111-111111111111'
export OWNER_ID='22222222-2222-4222-8222-222222222222'
export REVIEWER_ID='33333333-3333-4333-8333-333333333333'

export OWNER_TOKEN='owner-mobile-token'
export REVIEWER_TOKEN='reviewer-mobile-token'

export ASTRYNN_API_TOKENS_JSON='[
  {
    "token": "owner-mobile-token",
    "actor_id": "22222222-2222-4222-8222-222222222222",
    "organization_id": "11111111-1111-4111-8111-111111111111",
    "role": "CASE_OWNER",
    "display_name": "Mobile Owner"
  },
  {
    "token": "reviewer-mobile-token",
    "actor_id": "33333333-3333-4333-8333-333333333333",
    "organization_id": "11111111-1111-4111-8111-111111111111",
    "role": "REVIEWER",
    "display_name": "Mobile Reviewer"
  }
]'

export ASTRYNN_DATABASE_URL='sqlite:///./verification.db'
export ASTRYNN_AUTO_CREATE_SCHEMA='true'
```

### 3.3 Arrancar la API

```bash
uvicorn astrynn_devforge.api:app --host 0.0.0.0 --port 8000
```

Resultado esperado:

- Uvicorn inicia sin traceback.
- Puerto 8000 queda escuchando.
- `/health` responde.
- Swagger queda disponible en `/docs`.

Resultado observado: `PENDIENTE`

## 4. Primeros 8 endpoints del Anexo A

Abrir un segundo terminal del codespace. Mantener el primero ejecutando Uvicorn.

Base local:

```bash
export BASE_URL='http://127.0.0.1:8000'
```

### E-001 · Health

```bash
curl -sS -w '\nHTTP_STATUS=%{http_code}\n' "$BASE_URL/health"
```

Esperado:

- HTTP `200`.
- `status: ok`.
- `version: 0.6.0`.
- `authentication: bearer-rbac-development`.
- persistencia Kernel identificada.
- `oaaa_control_plane_persistence: in-memory-development`.

Resultado: `PENDIENTE`

Evidencia o notas:

```text
PENDIENTE
```

### E-002 · Identidad `/me`

```bash
curl -sS -w '\nHTTP_STATUS=%{http_code}\n' \
  -H "Authorization: Bearer $OWNER_TOKEN" \
  "$BASE_URL/api/v1/me"
```

Esperado:

- HTTP `200`.
- actor ID igual a `OWNER_ID`.
- organización igual a `ORG_ID`.
- rol `CASE_OWNER`.

Resultado: `PENDIENTE`

### E-003 · Crear caso

```bash
curl -sS -w '\nHTTP_STATUS=%{http_code}\n' \
  -o /tmp/create-case-response.txt \
  -H "Authorization: Bearer $OWNER_TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{\"title\":\"Caso sintético de verificación\",\"description\":\"Prueba humana de los primeros endpoints\",\"organization_id\":\"$ORG_ID\",\"sensitivity\":\"ORANGE\"}" \
  "$BASE_URL/api/v1/cases"

cat /tmp/create-case-response.txt
export CASE_ID=$(python -c 'import json; print(json.load(open("/tmp/create-case-response.txt"))["id"])')
echo "$CASE_ID"
```

Esperado:

- HTTP `201`.
- owner derivado del token, no del payload.
- organización correcta.
- estado inicial coherente.
- evento de creación presente.

Resultado: `PENDIENTE`

Case ID observado: `PENDIENTE`

### E-004 · Listar casos

```bash
curl -sS -w '\nHTTP_STATUS=%{http_code}\n' \
  -H "Authorization: Bearer $OWNER_TOKEN" \
  "$BASE_URL/api/v1/cases"
```

Esperado:

- HTTP `200`.
- lista contiene el caso creado.
- owner solo ve sus propios casos.

Resultado: `PENDIENTE`

### E-005 · Leer caso

```bash
curl -sS -w '\nHTTP_STATUS=%{http_code}\n' \
  -H "Authorization: Bearer $OWNER_TOKEN" \
  "$BASE_URL/api/v1/cases/$CASE_ID"
```

Esperado:

- HTTP `200`.
- ID, owner, organización, sensibilidad y eventos coinciden.

Resultado: `PENDIENTE`

### E-006 · Transición a `IN_REVIEW`

```bash
curl -sS -w '\nHTTP_STATUS=%{http_code}\n' \
  -H "Authorization: Bearer $OWNER_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"target":"IN_REVIEW","reason":"Ready for independent human verification"}' \
  "$BASE_URL/api/v1/cases/$CASE_ID/transition"
```

Esperado:

- HTTP `200`.
- estado `IN_REVIEW`.
- evento de transición trazable.

Resultado: `PENDIENTE`

### E-007 · Registrar aprobación independiente

```bash
curl -sS -w '\nHTTP_STATUS=%{http_code}\n' \
  -H "Authorization: Bearer $REVIEWER_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"decision":"APPROVE_WITH_CONDITIONS","rationale":"Bounded synthetic verification case","conditions":["Human approval before any external action"]}' \
  "$BASE_URL/api/v1/cases/$CASE_ID/approvals"
```

Esperado:

- HTTP `201`.
- approver derivado del token del reviewer.
- decision `APPROVE_WITH_CONDITIONS`.
- el owner no es el approver.

Resultado: `PENDIENTE`

### E-008 · Evaluar Aegis Clearance

```bash
curl -sS -w '\nHTTP_STATUS=%{http_code}\n' \
  -H "Authorization: Bearer $OWNER_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "title":"Document briefing assistant",
    "purpose":"Summarize approved synthetic documents for a named human reviewer",
    "sector":"professional_services",
    "scores":{
      "data":1,
      "permissions":1,
      "autonomy":1,
      "impact":1,
      "traceability":1,
      "human_oversight":1,
      "external_dependency":1,
      "adversarial_robustness":1,
      "incident_readiness":1
    },
    "data_categories":["synthetic_approved_documents"],
    "systems":["synthetic_document_repository"],
    "users":["named_reviewer"],
    "requested_actions":["draft_summary"],
    "providers":["external_llm"],
    "specialist_triggers":[],
    "critical_blockers":[]
  }' \
  "$BASE_URL/api/v1/aegis/cases/$CASE_ID/clearance/evaluate"
```

Esperado:

- HTTP `200`.
- decisión `APTO` para puntuación total 9 sin trigger ni blocker.
- total score `9`.
- nueve dimensiones presentes.
- Proof Receipt e input fingerprint presentes.
- no se aprueba ni activa el caso como efecto secundario.

Resultado: `PENDIENTE`

## 5. Resumen provisional

| Elemento | Estado |
|---|---|
| README permite instalar y ejecutar lint/tests | `DUDOSO · pendiente de ejecución humana` |
| README permite levantar API desde cero | `FALLA · documentación insuficiente` |
| API inicia | `PENDIENTE` |
| E-001 `/health` | `PENDIENTE` |
| E-002 `/api/v1/me` | `PENDIENTE` |
| E-003 crear caso | `PENDIENTE` |
| E-004 listar casos | `PENDIENTE` |
| E-005 leer caso | `PENDIENTE` |
| E-006 transición | `PENDIENTE` |
| E-007 aprobación | `PENDIENTE` |
| E-008 evaluar Clearance | `PENDIENTE` |

## 6. Criterio de cierre de esta primera parte

Esta parte del Bloque 0 solo podrá marcarse completada cuando:

1. una persona ejecute el entorno desde cero;
2. se registren versión, comandos, warnings y fricciones;
3. los ocho endpoints tengan respuesta y evidencia observada;
4. cualquier discrepancia se clasifique como `FALLA` o `DUDOSO`;
5. el README se corrija para permitir reproducción desde cero;
6. la verificación sea revisada y aceptada por una persona distinta del generador del código cuando corresponda.

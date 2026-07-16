# Block 0 · Deliberate Negative Controls

Fecha: 2026-07-16

Repositorio: `Sellynet/astrynn-devforge-gpt`

API evaluada: `0.6.0`

Estado: `22/22 FUNCIONA VERIFICADO`

## 1. Ejecución válida R-004

- Workflow: `Block 0 Deliberate Negative Verification`
- Run ID: `29496148880`
- Run number: `2`
- Commit evaluado: `883bcf5d93f9d0f7faa154dfb1d4439f699ed036`
- Fecha UTC: `2026-07-16T11:54:45Z`
- Runner: Ubuntu 24.04
- Python: `3.11.15`
- pip: `26.1.2`
- Ruff: `All checks passed!`
- pytest: `113 passed, 1 warning in 2.44s`
- Artifact: `block0-negative-verification-2`
- Artifact ID: `8374449620`
- Artifact SHA-256: `2911df6146ed80f7919ff31051497632d993dd415941c04a253cb47e1d7e4f4a`

No se utilizaron datos reales, secretos ni credenciales de clientes.

## 2. Resultado resumido

| ID | Intento deliberado | Respuesta esperada | Estado |
|---|---|---:|---|
| N-001 | Acceder sin token | 401 | `FUNCIONA VERIFICADO` |
| N-002 | Usar token inválido | 401 | `FUNCIONA VERIFICADO` |
| N-003 | Inyectar `actor_id` y `owner_id` | 422 | `FUNCIONA VERIFICADO` |
| N-004 | Crear caso para otra organización | 403 | `FUNCIONA VERIFICADO` |
| N-005 | Leer caso de otra organización | 403 | `FUNCIONA VERIFICADO` |
| N-006 | Autoaprobar el propio caso | 403 | `FUNCIONA VERIFICADO` |
| N-007 | Owner intenta activar el caso | 403 | `FUNCIONA VERIFICADO` |
| N-008 | Saltar de `DRAFT` a `ACTIVE` | 409 | `FUNCIONA VERIFICADO` |
| N-009 | Owner registra Clearance final | 403 | `FUNCIONA VERIFICADO` |
| N-010 | Score Aegis fuera de 0–5 | 422 | `FUNCIONA VERIFICADO` |
| N-011 | Specialist trigger con score bajo | 200 + revisión especializada | `FUNCIONA VERIFICADO` |
| N-012 | Critical blocker con score bajo | 200 + no apto todavía | `FUNCIONA VERIFICADO` |
| N-013 | Viewer intenta evaluar Clearance | 403 | `FUNCIONA VERIFICADO` |
| N-014 | Owner registra Atlas final | 403 | `FUNCIONA VERIFICADO` |
| N-015 | Atlas recibe referencia de fuente inexistente | 422 | `FUNCIONA VERIFICADO` |
| N-016 | OAAA recibe identidad falsificable | 422 | `FUNCIONA VERIFICADO` |
| N-017 | Segundo owner diseña sobre caso ajeno | 403 | `FUNCIONA VERIFICADO` |
| N-018 | OAAA recibe wildcard de tool | 422 | `FUNCIONA VERIFICADO` |
| N-019 | OAAA recibe plan ARIA incompleto | 422 | `FUNCIONA VERIFICADO` |
| N-020 | Envío OAAA duplicado | 409 | `FUNCIONA VERIFICADO` |
| N-021 | Intento de endpoint OAAA `activate` | 404 | `FUNCIONA VERIFICADO` |
| N-022 | Lectura cross-organization de blueprint | 403 | `FUNCIONA VERIFICADO` |

## 3. Evidencia de controles

### Autenticación e identidad

Se confirmó que:

- los endpoints protegidos exigen Bearer token;
- un token inexistente no autentica;
- `actor_id`, `owner_id` y `organization_id` no pueden falsificarse desde el payload;
- la identidad y el ámbito se derivan del principal autenticado y del caso.

### Separación organizativa

Se confirmó que:

- un owner no puede crear recursos para otra organización;
- un actor no puede leer casos o blueprints de otra organización;
- dos owners de una misma organización siguen separados a nivel de ownership del caso.

### Separación de funciones

Se confirmó que:

- el owner no puede autoaprobar;
- el owner no puede registrar el Clearance final;
- el owner no puede registrar el briefing Atlas final;
- un viewer no puede evaluar Aegis;
- el owner no puede activar casos directamente.

### Integridad de estados

Se confirmó que:

- `DRAFT → ACTIVE` no es una transición válida;
- un blueprint no puede enviarse dos veces a revisión;
- OAAA no expone un endpoint de activación.

### Aegis

Se confirmó que:

- los scores fuera de rango se rechazan;
- un specialist trigger prevalece sobre un score numérico bajo;
- un critical blocker impide una decisión `APTO`;
- las decisiones observadas fueron `REQUIERE_REVISION_ESPECIALIZADA` y `NO_APTO_TODAVIA` respectivamente.

### Atlas

Se confirmó que:

- referencias a fuentes inexistentes se rechazan;
- la producción final de evidencia permanece separada del owner.

### OAAA

Se confirmó que:

- se rechazan campos de identidad añadidos al payload;
- se rechazan wildcards en operaciones de tools;
- se exige la familia ARIA `INCIDENT_TRIGGER`;
- se respeta ownership y aislamiento organizativo;
- no existe ruta de activación.

## 4. Ejecución R-003N descartada

La primera ejecución del workflow negativo, Run ID `29495923583`, produjo:

- 21 controles verificados;
- 1 control clasificado como fallo;
- HTTP 403 correcto en el control N-013.

La respuesta observada fue:

`Role VIEWER lacks AEGIS_EVALUATE`

El verificador esperaba erróneamente que el detalle contuviera la palabra genérica `permission`. Se corrigió el criterio para comprobar la semántica real `lacks AEGIS_EVALUATE`.

Clasificación: `FALLA DEL HARNESS DE VERIFICACIÓN · CORREGIDA`.

No se considera un defecto funcional de la API.

## 5. Límites

Esta ejecución no demuestra todavía:

- persistencia después de reiniciar Uvicorn;
- persistencia OAAA;
- PostgreSQL/Supabase;
- identidad productiva;
- runtime de agentes;
- integraciones externas;
- resistencia de un modelo o agente real a prompt injection;
- cumplimiento regulatorio ni certificación.

## 6. Conclusión

Los 22 controles negativos definidos para este tramo del Bloque 0 quedan como `FUNCIONA VERIFICADO` en una ejecución reproducible contra la API real levantada con Uvicorn y datos sintéticos.

El siguiente tramo obligatorio es verificar persistencia después de reinicio, documentando por separado lo que sobrevive en Kernel SQLite y la pérdida esperada del control plane OAAA en memoria.

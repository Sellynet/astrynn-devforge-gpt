# VERIFICATION.md · Bloque 0 · Verificación humana del prototipo

Fecha de apertura: 2026-07-16

Repositorio: `Sellynet/astrynn-devforge-gpt`

Rama de trabajo: `verification/block-0-readme-and-first-8-endpoints`

Estado global: `BLOQUE 0 PARCIALMENTE COMPLETADO`

## 1. Regla de evidencia

Estados permitidos:

- `FUNCIONA VERIFICADO`: ejecución reproducible completada y evidencia revisada.
- `FALLA`: el comportamiento observado contradice el resultado esperado o impide continuar.
- `DUDOSO`: evidencia incompleta, ambigua o no reproducida.
- `PENDIENTE`: prueba todavía no ejecutada.

Una CI verde no cierra por sí sola todo el Bloque 0. La ejecución automatizada aporta evidencia reproducible, pero siguen pendientes la lectura humana de tests, las pruebas negativas deliberadas, la persistencia tras reinicio y la revisión de PostgreSQL/Supabase.

No se utilizaron datos reales, secretos ni credenciales de clientes.

## 2. Alcance verificado en esta entrega

Esta primera entrega cubre:

1. preparación de un entorno limpio con Python 3.11;
2. instalación mediante los comandos disponibles en el README;
3. ejecución de Ruff;
4. ejecución de la suite pytest;
5. arranque real de la API con Uvicorn;
6. persistencia SQLite sintética para la prueba manual;
7. verificación de los primeros ocho endpoints del Anexo A;
8. generación de artefactos con logs, respuestas JSON e informe Markdown.

## 3. Ejecución válida R-002

- Workflow: `Block 0 Human Verification`
- Run ID: `29487356386`
- Run number: `2`
- Commit evaluado: `4bf36d85f378b01e13ef7209361fd50aa8e5960f`
- Fecha UTC: `2026-07-16T09:30:08Z`
- Runner: Ubuntu 24.04
- Python: `3.11.15`
- pip: `26.1.2`
- Artifact: `block0-human-verification-2`
- Artifact ID: `8370940305`
- Artifact SHA-256: `4ed3836f406b6567cb775c0f30df54e3cc492f327f9757ec293d1cf9f60749ef`

### Resultado del pipeline

| Etapa | Resultado |
|---|---|
| Entorno limpio | `FUNCIONA VERIFICADO` |
| Instalación con comandos del README | `FUNCIONA VERIFICADO` |
| Ruff | `FUNCIONA VERIFICADO` |
| pytest | `FUNCIONA VERIFICADO` |
| Arranque de la API | `FUNCIONA VERIFICADO` |
| Primeros ocho endpoints | `FUNCIONA VERIFICADO` |

### Calidad automática

- Ruff: `All checks passed!`
- pytest: `113 passed, 1 warning in 2.55s`
- Warning observado: `StarletteDeprecationWarning` sobre el uso actual de `httpx` con `starlette.testclient`.
- Clasificación del warning: `DUDOSO · deuda técnica no bloqueante, pendiente de revisión`.

## 4. Primeros ocho endpoints

| ID | Endpoint | HTTP esperado | HTTP observado | Estado |
|---|---|---:|---:|---|
| E-001 | `GET /health` | 200 | 200 | `FUNCIONA VERIFICADO` |
| E-002 | `GET /api/v1/me` | 200 | 200 | `FUNCIONA VERIFICADO` |
| E-003 | `POST /api/v1/cases` | 201 | 201 | `FUNCIONA VERIFICADO` |
| E-004 | `GET /api/v1/cases` | 200 | 200 | `FUNCIONA VERIFICADO` |
| E-005 | `GET /api/v1/cases/{case_id}` | 200 | 200 | `FUNCIONA VERIFICADO` |
| E-006 | `POST /api/v1/cases/{case_id}/transition` | 200 | 200 | `FUNCIONA VERIFICADO` |
| E-007 | `POST /api/v1/cases/{case_id}/approvals` | 201 | 201 | `FUNCIONA VERIFICADO` |
| E-008 | `POST /api/v1/aegis/cases/{case_id}/clearance/evaluate` | 200 | 200 | `FUNCIONA VERIFICADO` |

### Evidencia funcional clave

#### E-001 · Health

Se observó:

- `status: ok`;
- versión `0.6.0`;
- persistencia `sqlalchemy-sqlite`;
- autenticación `bearer-rbac-development`;
- OAAA control plane en `in-memory-development`.

#### E-002 · Identidad

El token sintético de owner devolvió:

- actor ID esperado;
- organization ID esperado;
- rol `CASE_OWNER`.

#### E-003 · Crear caso

Se verificó:

- creación HTTP 201;
- owner derivado del token;
- organización correcta;
- estado inicial `DRAFT`;
- evento `CASE_CREATED` presente.

#### E-004 y E-005 · Listar y leer

Se verificó:

- el owner recupera el caso creado;
- la respuesta conserva owner, organización y sensibilidad;
- el listado del owner queda limitado a sus propios casos dentro del escenario sintético.

#### E-006 · Transición

Se verificó:

- transición `DRAFT → IN_REVIEW`;
- respuesta HTTP 200;
- evento `STATUS_CHANGED` trazable;
- reason conservado.

#### E-007 · Aprobación independiente

Se verificó:

- respuesta HTTP 201;
- approver derivado del token del reviewer;
- decisión `APPROVE_WITH_CONDITIONS`;
- identidades owner y reviewer separadas.

#### E-008 · Aegis Clearance

Se verificó:

- decisión `APTO`;
- puntuación total `9`;
- nueve dimensiones evaluadas;
- `input_fingerprint` presente;
- metodología `AEGIS-CLEARANCE-0.1`;
- la evaluación no aprobó ni activó el caso como efecto secundario;
- el caso permaneció en `IN_REVIEW`.

## 5. Ejecución R-001 descartada como evidencia final

La primera ejecución, Run ID `29487147734`, produjo:

- Ruff correcto;
- API correcta;
- 8/8 endpoints correctos;
- pytest con `111 passed, 2 failed`.

La causa fue una contaminación introducida por el propio workflow: `ASTRYNN_DATABASE_URL` se aplicó globalmente a toda la suite, haciendo que distintos tests compartieran el mismo archivo SQLite y acumularan casos.

Corrección aplicada:

- pytest vuelve a ejecutarse con su configuración aislada por defecto;
- SQLite y los tokens sintéticos quedan limitados al paso de arranque de la API;
- la segunda ejecución completó `113 passed`.

Clasificación: `FALLA DEL HARNESS DE VERIFICACIÓN · CORREGIDA`.

No se considera evidencia de un defecto funcional del Kernel.

## 6. Hallazgo documental del README

Estado: `FALLA · DOCUMENTACIÓN INSUFICIENTE`

El README sí permite instalar dependencias y ejecutar Ruff/pytest, pero no contiene todavía un recorrido completo desde repositorio limpio hasta API operativa.

Faltan, como mínimo:

1. instrucciones de clonado y directorio de trabajo;
2. creación y activación de entorno virtual;
3. comprobación de Python 3.11 o superior;
4. comando Uvicorn;
5. formato de `ASTRYNN_API_TOKENS_JSON`;
6. configuración de `ASTRYNN_DATABASE_URL`;
7. comportamiento de `ASTRYNN_AUTO_CREATE_SCHEMA`;
8. URL de Swagger;
9. separación de identidades owner/reviewer;
10. procedimiento de cierre, reinicio y comprobación de persistencia.

Además, el README sigue describiendo la fase como `fundación técnica y Kernel mínimo`, mientras el paquete y la API declaran versión `0.6.0`.

Conclusión: el código puede levantarse con el runbook suplementario, pero una persona nueva no puede reproducir todo el recorrido siguiendo únicamente el README.

## 7. Evidencia técnica conservada

El workflow conserva durante 30 días:

- `environment.txt`;
- `install.txt`;
- `ruff.txt`;
- `pytest.txt`;
- `uvicorn.log`;
- `endpoint-console.txt`;
- `block0-endpoint-results.json`;
- `block0-endpoint-results.md`;
- `actions-summary.md`.

El resumen permanente de la ejecución se encuentra en:

`docs/verification/BLOCK0_FIRST_8_ENDPOINTS_2026-07-16.md`

## 8. Pendientes para cerrar el Bloque 0 completo

1. Corregir el README y repetir el levantamiento siguiendo solo esa documentación.
2. Leer manualmente los tests y evaluar si prueban comportamiento real o solo implementación.
3. Ejecutar fallos deliberados:
   - token ausente;
   - token inválido;
   - acceso cross-organization;
   - owner intentando aprobar;
   - owner intentando activar;
   - transición inválida;
   - score fuera de rango;
   - blocker crítico;
   - specialist trigger.
4. Reiniciar la API y verificar persistencia SQLite.
5. Repetir persistencia con PostgreSQL/Supabase.
6. Revisar los gaps entre Pull Requests y commits.
7. Resolver o aceptar formalmente el warning de Starlette/httpx.
8. Obtener revisión humana nominal de esta evidencia.

## 9. Conclusión de esta entrega

La instalación, la suite automática, el arranque real de la API y los primeros ocho endpoints quedan como `FUNCIONA VERIFICADO` dentro del entorno reproducible de GitHub Actions.

El Bloque 0 completo no está cerrado. El principal hallazgo abierto de esta primera parte es documental: el README todavía no permite reproducir el sistema desde cero sin conocimiento adicional.

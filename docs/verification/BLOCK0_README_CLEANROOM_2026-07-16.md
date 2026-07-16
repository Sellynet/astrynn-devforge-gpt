# Block 0 · README clean-room verification

Fecha UTC: 2026-07-16

## Resultado

Clasificación: **FUNCIONA VERIFICADO · CLEAN-ROOM AUTOMATIZADO**

El workflow extrajo el bloque ejecutable directamente de `README.md` y lo ejecutó en un directorio limpio. No utilizó los verificadores HTTP anteriores para realizar el recorrido.

## Ejecución válida

- Workflow: `Block 0 README Clean-room Verification`
- Run ID: `29504297700`
- Run number: `1`
- Rama clonada: `verification/block-0-readme-cleanroom`
- Head de la rama: `bcf0301f622794239334797a3e81da1aef308b95`
- Python: `3.11.15`
- Ruff: `All checks passed!`
- pytest: `113 passed, 1 warning in 2.55s`
- Artifact: `block0-readme-cleanroom-1`
- Artifact ID: `8377786643`
- Artifact SHA-256: `9e8102a0de3a34d0a8426a2418b063a585e31774f6519afc9aca30e5712fae86`

## Pasos observados

1. El repositorio fue clonado mediante `git clone --depth 1 --branch`.
2. Se creó un entorno virtual nuevo.
3. Se actualizó pip y se instaló el paquete editable con Ruff y pytest.
4. Ruff terminó correctamente.
5. La suite terminó con 113 tests superados.
6. Uvicorn arrancó con SQLite local y dos identidades Bearer sintéticas.
7. Se recorrieron los primeros ocho endpoints mediante HTTP real.
8. Se guardaron ocho respuestas JSON y el log de Uvicorn.

## Primeros ocho endpoints

| ID | Endpoint | Esperado | Observado | Estado |
|---|---|---:|---:|---|
| E-001 | `GET /health` | 200 | 200 | `FUNCIONA VERIFICADO` |
| E-002 | `GET /api/v1/me` | 200 | 200 | `FUNCIONA VERIFICADO` |
| E-003 | `POST /api/v1/cases` | 201 | 201 | `FUNCIONA VERIFICADO` |
| E-004 | `GET /api/v1/cases` | 200 | 200 | `FUNCIONA VERIFICADO` |
| E-005 | `GET /api/v1/cases/{case_id}` | 200 | 200 | `FUNCIONA VERIFICADO` |
| E-006 | `POST /api/v1/cases/{case_id}/transition` | 200 | 200 | `FUNCIONA VERIFICADO` |
| E-007 | `POST /api/v1/cases/{case_id}/approvals` | 201 | 201 | `FUNCIONA VERIFICADO` |
| E-008 | `POST /api/v1/aegis/cases/{case_id}/clearance/evaluate` | 200 | 200 | `FUNCIONA VERIFICADO` |

## Semántica confirmada

- la transición produjo `IN_REVIEW`;
- la aprobación produjo `APPROVE_WITH_CONDITIONS`;
- Aegis produjo `APTO`;
- la puntuación total fue `9`;
- `/health` declaró `sqlalchemy-sqlite`;
- `/health` declaró OAAA como `in-memory-development`.

## Fricciones anotadas

### F-README-001 · Warning de dependencias

Clasificación: `DUDOSO · DEUDA TÉCNICA NO BLOQUEANTE`

pytest emitió un `StarletteDeprecationWarning` sobre la integración actual entre `httpx` y `starlette.testclient`. No impidió la ejecución.

### F-README-002 · Presentación cosmética de la ruta de evidencia

Clasificación: `DUDOSO · COSMÉTICO NO BLOQUEANTE`

El workflow proporcionó `EVIDENCE_DIR` como ruta absoluta. El mensaje final del bloque concatenó el directorio de trabajo y esa ruta al imprimirla. Los archivos se guardaron y subieron correctamente en la ubicación absoluta esperada.

### F-README-003 · Ejecución humana nominal

Clasificación: `PENDIENTE`

La clean-room demuestra reproducibilidad automatizada. No sustituye una observación humana nominal en Swagger ni una ejecución en el ordenador físico de una persona siguiendo el README.

## Conclusión

La deficiencia documental original queda corregida para la ruta Linux, macOS o WSL y verificada en un runner Ubuntu limpio. El README contiene ahora clonación, entorno virtual, instalación, variables, SQLite, Uvicorn, Swagger, primeros ocho endpoints, reinicio, persistencia, fricciones y límites.

Queda pendiente una pasada humana nominal en Swagger para cerrar literalmente la instrucción de prueba manual.
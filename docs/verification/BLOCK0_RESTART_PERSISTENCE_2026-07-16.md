# Block 0 · Restart Persistence Verification

Fecha: 2026-07-16

Estado: `20/20 FUNCIONA VERIFICADO`

## Ejecución válida R-005

- Workflow: `Block 0 Restart Persistence Verification`
- Run ID: `29499245290`
- Run number: `5`
- Head de la rama: `7b5feda97ac744106cf689320627d2cf72fc32f9`
- Commit evaluado por Actions: `18cde36c0dd3d14e941ff88c274d53e38cfb4563`
- Fecha UTC: `2026-07-16T12:43:26Z`
- Runner: Ubuntu 24.04
- Python: `3.11.15`
- pip: `26.1.2`
- Ruff: `All checks passed!`
- pytest: `113 passed, 1 warning in 2.58s`
- Artifact: `block0-restart-persistence-5`
- Artifact ID: `8375700175`
- Artifact SHA-256: `4bbfc58d7aa57bb1876dd00e102cb2c957a0c398d2b48e899321e3eabc39d7c0`
- SQLite SHA-256: `07714892ca70cd0b76fee4532618bb36c444c8656ebed6195fa905c8808c80fb`

## Método

La verificación utilizó dos procesos Uvicorn distintos y el mismo archivo SQLite.

### Primer proceso

1. Crear un caso `ORANGE` sintético.
2. Transicionar `DRAFT → IN_REVIEW`.
3. Registrar aprobación independiente.
4. Transicionar a `APPROVED`.
5. Registrar Aegis Clearance y Proof Receipt.
6. Registrar briefing Atlas y Proof Receipt.
7. Crear blueprint OAAA v1 `DRAFT`.
8. Enviar blueprint OAAA v2 a `IN_REVIEW`.
9. Capturar el snapshot público y el snapshot SQLAlchemy.
10. Detener completamente Uvicorn y confirmar que el puerto deja de responder.

### Segundo proceso

1. Arrancar Uvicorn con `ASTRYNN_AUTO_CREATE_SCHEMA=false`.
2. Reutilizar exactamente el mismo archivo SQLite.
3. Recuperar el caso mediante API.
4. Recuperar caso, eventos, aprobación, outputs y evidencias mediante SQLAlchemy.
5. Consultar físicamente las tablas SQLite.
6. Intentar recuperar el blueprint OAAA anterior.
7. Volver a evaluar el caso con Aegis.

## Resultado de los 20 controles

| Grupo | Resultado |
|---|---|
| Primer proceso y creación de estado | `10/10 FUNCIONA VERIFICADO` |
| Segundo proceso y recuperación pública | `5/5 FUNCIONA VERIFICADO` |
| Recuperación SQLAlchemy y SQLite física | `5/5 FUNCIONA VERIFICADO` |
| Total | `20/20 FUNCIONA VERIFICADO` |

## Estado durable confirmado

Después del reinicio se recuperaron sin cambios:

- el mismo case ID;
- estado `APPROVED`;
- versión interna Kernel `5`;
- los mismos cuatro eventos y sus IDs;
- una aprobación independiente con el mismo ID;
- cuatro outputs con los mismos IDs;
- seis referencias de evidencia con los mismos IDs.

Las filas físicas del caso fueron:

```json
{
  "cases": 1,
  "events": 4,
  "approvals": 1,
  "outputs": 4,
  "evidence": 6
}
```

Los conteos posteriores coincidieron exactamente con el baseline capturado antes del apagado.

## Aegis y Atlas

Persistieron:

- `AEGIS_CLEARANCE_REPORT`;
- `ORBYN_ATLAS_BRIEFING`;
- Aegis Clearance Proof Receipt;
- Orbyn Atlas Briefing Proof Receipt.

El caso recuperado volvió a evaluarse correctamente con:

- decisión `APTO`;
- puntuación total `9`.

## Frontera OAAA observada

El endpoint del blueprint anterior respondió después del reinicio:

```text
HTTP 404 · Blueprint not found
```

Esto confirma que el repositorio operativo de blueprints continúa siendo `in-memory-development`.

Sin embargo, el Kernel sí conservó el rastro de auditoría generado por OAAA:

- dos outputs `OAAA_AGENT_BLUEPRINT`, versiones 1 y 2;
- evidencias de Output Vault para ambas versiones;
- evidencias OAAA para `DRAFT v1` e `IN_REVIEW v2`.

Conclusión precisa:

- `estado operativo OAAA`: volátil;
- `rastro de auditoría OAAA en Kernel`: persistente.

## Ejecuciones descartadas

### Run 1 · ID 29498525073

Problemas del harness:

- `ASTRYNN_DATABASE_URL` se aplicó globalmente y contaminó pytest;
- el script intentó leer `version` e IDs de eventos desde `CaseResponse`, campos no expuestos por la API pública.

Clasificación: `FALLA DEL HARNESS · CORREGIDA`.

### Run 3 · ID 29498940953

La recuperación funcionó en 19 de 20 controles. El único fallo fue una expectativa incorrecta del harness:

- esperaba 2 outputs y 2 evidencias;
- encontró 4 outputs y 6 evidencias porque OAAA también registra artefactos y trazas durables en Kernel.

Clasificación: `EXPECTATIVA DEL HARNESS INCORRECTA · CORREGIDA`.

## Límites

Esta verificación no demuestra:

- persistencia operativa de blueprints OAAA;
- PostgreSQL o Supabase;
- concurrencia entre procesos o runners;
- migraciones de esquema;
- identidad productiva;
- Output Vault productivo independiente;
- runtime o despliegue de agentes;
- integraciones externas.

## Conclusión

La persistencia Kernel basada en SQLite queda verificada entre dos procesos Uvicorn distintos para casos, eventos, aprobaciones, outputs y evidencias.

OAAA conserva un rastro de auditoría durable, pero no conserva todavía el blueprint operativo tras el reinicio. Esta limitación queda demostrada y documentada, no inferida.
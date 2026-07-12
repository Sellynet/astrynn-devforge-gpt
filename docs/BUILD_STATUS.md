# Build Status · Orbyn Atlas + Aegis

Última actualización: 2026-07-12

## Estado de módulos

| Módulo | Estado | Evidencia |
|---|---|---|
| Fundación y doctrina | COMPLETADO | PR #9 |
| Kernel mínimo v0.1 | COMPLETADO | PR #10 |
| Aegis Deployment Clearance v0.1 | COMPLETADO | PR #11 |
| Orbyn Atlas Case + Briefing v0.1 | COMPLETADO | PR #12 |
| Output Vault + Proof Receipt v0.1 | COMPLETADO | PR #13 |
| OAAA Agent Blueprint v0.1 | COMPLETADO | PR #14 |
| ARIA Test Register v0.1 | COMPLETADO | PR #16 |
| Vigilance Permissions Layer v0.1 | COMPLETADO | PR #17 |
| Private API + persistencia de desarrollo v0.1 | COMPLETADO | PR #20 |
| Autenticación Bearer + RBAC organizativo v0.2 | COMPLETADO | PR #22 |
| SQLAlchemy + SQLite/PostgreSQL/Supabase v0.3 | COMPLETADO | PR #24 |
| Aegis Deployment Clearance API v0.4 | COMPLETADO | PR #27 |
| Orbyn Atlas Briefing API v0.5 | COMPLETADO | PR #29 |
| OAAA Agent Blueprint Design API v0.6 | IMPLEMENTADO | Esta PR |
| ARIA Test Register API | SIGUIENTE | Pendiente |
| Vigilance Permissions API | PENDIENTE | Pendiente |
| Frontend privado móvil | PENDIENTE | Pendiente |
| Persistencia OAAA/Output Vault, migraciones, RLS e identidad de producción | PENDIENTE | Pendiente |
| Despliegue privado controlado | PENDIENTE | Pendiente |

## Estado operativo real

- El dominio, los controles y la API privada ya existen como software probado.
- Los casos pueden sobrevivir al reinicio de la aplicación mediante SQLite o PostgreSQL/Supabase.
- La identidad del actor deriva del Bearer token autenticado y no se acepta desde el payload.
- Los roles y el aislamiento lógico por organización están implementados.
- Aegis puede evaluar y registrar Clearance Reports y Proof Receipts sin aprobar ni activar casos.
- Orbyn Atlas puede construir y registrar briefings trazables sin obtener datos externos ni controlar infraestructura.
- OAAA puede crear, leer, versionar y enviar Agent Blueprints a revisión mediante API privada.
- La API OAAA termina deliberadamente en `IN_REVIEW`: no expone clearance, aprobación, activación, credenciales, ejecución ni despliegue.
- El repositorio Kernel puede ser persistente, pero el control plane OAAA y Output Vault usado por la API v0.6 sigue siendo `in-memory-development`.
- La API todavía no debe exponerse públicamente: faltan identidad de producción, persistencia OAAA/Output Vault, migraciones revisadas, RLS, gestión de secretos, backups y revisión de despliegue.
- PostgreSQL/Supabase está soportado como backend Kernel, pero no se ha conectado ninguna credencial ni base real desde este repositorio público.

## Cómo comprobar el trabajo desde el móvil

1. Abrir el repositorio `Sellynet/astrynn-devforge-gpt`.
2. Entrar en **Pull requests** para ver cada bloque construido y sus archivos.
3. Entrar en **Actions** para comprobar que `ruff` y `pytest` terminan en verde.
4. Entrar en **Issues** para revisar el backlog y qué tarea está abierta o cerrada.
5. En la pestaña **Code**, abrir `docs/` para leer arquitectura, límites y metodología.
6. Abrir `tests/` para ver exactamente qué comportamientos están comprobados.
7. Abrir `docs/AUTH_RBAC_V0_2.md` para revisar autenticación y separación de funciones.
8. Abrir `docs/PERSISTENCE_POSTGRES_SUPABASE_V0_3.md` para revisar persistencia.
9. Abrir `docs/AEGIS_CLEARANCE_API_V0_4.md` para revisar la API de assurance.
10. Abrir `docs/ATLAS_BRIEFING_API_V0_5.md` para revisar la API de inteligencia operativa.
11. Abrir `docs/OAAA_AGENT_BLUEPRINT_API_V0_6.md` para revisar la API de diseño gobernado de agentes.
12. Ejecutar la API localmente y abrir `http://127.0.0.1:8000/docs` para usar Swagger.

## Regla de lectura

- **Merged** significa incorporado a `main`.
- **Closed issue** significa criterio de aceptación completado.
- **Green Actions run** significa que lint y tests automáticos pasaron.
- `ACTIVE` en OAAA es un estado de gobierno, no un despliegue de software.
- `ALLOWED` en Vigilance es una autorización registrada, no una ejecución externa.
- Compatibilidad con PostgreSQL/Supabase no significa despliegue productivo ni conexión a datos reales.
- Un briefing Atlas es apoyo a decisión, no una autorización Aegis ni una orden operativa.
- Un blueprint OAAA es un diseño gobernado, no un agente conectado ni ejecutándose.

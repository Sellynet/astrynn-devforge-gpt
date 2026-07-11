# Build Status · Orbyn Atlas + Aegis

Última actualización: 2026-07-11

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
| Autenticación y roles | SIGUIENTE | Pendiente |
| PostgreSQL/Supabase | PENDIENTE | Pendiente |
| Frontend privado | PENDIENTE | Pendiente |

## Cómo comprobar el trabajo desde el móvil

1. Abrir el repositorio `Sellynet/astrynn-devforge-gpt`.
2. Entrar en **Pull requests** para ver cada bloque construido y sus archivos.
3. Entrar en **Actions** para comprobar que `ruff` y `pytest` terminan en verde.
4. Entrar en **Issues** para revisar el backlog y qué tarea está abierta o cerrada.
5. En la pestaña **Code**, abrir `docs/` para leer arquitectura, límites y metodología.
6. Abrir `tests/` para ver exactamente qué comportamientos están comprobados.
7. Abrir `docs/PRIVATE_API_V0_1.md` para ejecutar la API localmente.
8. Abrir `http://127.0.0.1:8000/docs` cuando la API esté ejecutándose para usar Swagger.

## Regla de lectura

- **Merged** significa incorporado a `main`.
- **Closed issue** significa criterio de aceptación completado.
- **Green Actions run** significa que lint y tests automáticos pasaron.
- `ACTIVE` en OAAA es un estado de gobierno, no un despliegue de software.
- `ALLOWED` en Vigilance es una autorización registrada, no una ejecución externa.
- La API v0.1 no debe exponerse públicamente hasta incorporar autenticación, persistencia segura y revisión de despliegue.

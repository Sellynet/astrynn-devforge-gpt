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
| ARIA Test Register | PENDIENTE | Issue #6 |
| Vigilance Permissions Layer | PENDIENTE | Issue #7 |

## Cómo comprobar el trabajo desde el móvil

1. Abrir el repositorio `Sellynet/astrynn-devforge-gpt`.
2. Entrar en **Pull requests** para ver cada bloque construido y sus archivos.
3. Entrar en **Actions** para comprobar que `ruff` y `pytest` terminan en verde.
4. Entrar en **Issues** para revisar el backlog y qué tarea está abierta o cerrada.
5. En la pestaña **Code**, abrir `docs/` para leer arquitectura, límites y metodología.
6. Abrir `tests/` para ver exactamente qué comportamientos están comprobados.
7. Abrir `examples/atlas_demo.py` para ver un caso sintético completo de Atlas.
8. Abrir `examples/output_vault_demo.py` para ver versionado, decisión y Proof Receipt.
9. Abrir `examples/oaaa_blueprint_demo.py` para ver el ciclo gobernado de un agente.

## Regla de lectura

- **Merged** significa incorporado a `main`.
- **Closed issue** significa criterio de aceptación completado.
- **Green Actions run** significa que lint y tests automáticos pasaron.
- `ACTIVE` en OAAA es un estado de gobierno, no un despliegue de software.
- Ningún módulo se considera producto desplegado hasta que exista aplicación, persistencia y entorno de piloto aprobados.

# Private API v0.1

Primera capa HTTP sobre el Kernel de Orbyn Atlas + Aegis.

## Ejecutar localmente

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e . ruff pytest
uvicorn astrynn_devforge.api.app:app --reload
```

Abrir:

- API: `http://127.0.0.1:8000`
- OpenAPI: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## Endpoints iniciales

```text
GET  /health
POST /api/v1/cases
GET  /api/v1/cases
GET  /api/v1/cases/{case_id}
POST /api/v1/cases/{case_id}/transition
POST /api/v1/cases/{case_id}/approvals
```

## Persistencia

La versión 0.1 utiliza `InMemoryKernelRepository`. Los datos se pierden al reiniciar el proceso. Esta decisión permite validar el contrato HTTP antes de introducir PostgreSQL/Supabase.

## Seguridad y límites

- No existe autenticación real todavía.
- No debe exponerse públicamente.
- No contiene secretos.
- No ejecuta acciones externas.
- No despliega agentes.
- No conecta sistemas críticos.
- Todas las reglas de estados y aprobaciones siguen viviendo en el Kernel, no en las rutas HTTP.

## Próxima evolución

1. autenticación y roles;
2. PostgreSQL/Supabase;
3. migraciones;
4. endpoints Aegis, Atlas, OAAA, ARIA y Vigilance;
5. frontend privado.

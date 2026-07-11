# Astrynn DevForge · Orbyn Atlas + Aegis

Repositorio de construcción controlada para:

- **Orbyn Atlas**, inteligencia operativa para infraestructuras, territorios y ecosistemas estratégicos.
- **Aegis AI Assurance Guardian**, evaluación, Deployment Clearance, guardrails, evidencia, ARIA e incident readiness.
- **Orbyn Adaptive Agent Architecture (OAAA)**, diseño y ensamblaje gobernado de agentes específicos para cada organización.

## Regla central

Los agentes pueden proponer y ensamblar nuevos agentes, pero no pueden autoautorizarse, elevar sus permisos ni desplegarse en producción sin Aegis Clearance, pruebas ARIA, controles Vigilance y aprobación humana nominal.

## Estado

**Fase actual:** fundación técnica y Kernel mínimo.

## Documentación de control

- [`docs/BUILD_CONTROL_ORBYN_ATLAS_AEGIS.md`](docs/BUILD_CONTROL_ORBYN_ATLAS_AEGIS.md)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/MVP_SCOPE.md`](docs/MVP_SCOPE.md)
- [`docs/SECURITY_AND_APPROVAL_GATES.md`](docs/SECURITY_AND_APPROVAL_GATES.md)
- [`docs/adr/0001-implementation-architecture.md`](docs/adr/0001-implementation-architecture.md)
- [`tasks/BACKLOG.md`](tasks/BACKLOG.md)

## Arquitectura decidida

Monorepo evolutivo:

- núcleo de dominio en Python 3.11;
- API FastAPI cuando los contratos estén estabilizados;
- frontend Next.js + TypeScript + Tailwind;
- persistencia local durante desarrollo y Supabase/PostgreSQL para pilotos;
- despliegue privado posterior detrás de Cloudflare y Nginx sobre VPS.

## Calidad

```bash
python -m pip install --upgrade pip
pip install -e . ruff pytest
ruff check .
pytest -q
```

Todo módulo debe entrar mediante rama y Pull Request, con pruebas, aprobación y evidencia. Aquí el código no corre suelto por el pasillo con unas tijeras. 🛡️

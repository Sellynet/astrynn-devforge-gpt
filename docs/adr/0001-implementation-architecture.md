# ADR 0001 · Arquitectura de implementación

- **Estado:** Aceptada
- **Fecha:** 2026-07-11
- **Ámbito:** Orbyn Atlas + Aegis AI Assurance Guardian + OAAA

## Contexto

El repositorio existente ya contiene un núcleo Python mínimo, pruebas con `pytest` y control de calidad con `ruff`. La arquitectura de producto requiere además una interfaz web privada, rutas Atlas/Aegis/OAAA, persistencia, evidencia versionada y despliegue posterior sobre VPS con Cloudflare.

La prioridad es construir rápido sin crear dos sistemas desconectados ni una plataforma sobredimensionada antes de validar pilotos.

## Decisión

Se adopta un **monorepo evolutivo** con dos capas:

```text
apps/
  web/                 # Next.js + TypeScript + Tailwind, fase posterior inmediata
src/astrynn_devforge/
  kernel/              # dominio, estados, aprobaciones, evidencia
  aegis/               # Clearance, guardrails, ARIA, incident readiness
  atlas/               # casos, señales, riesgos, escenarios, briefings
  oaaa/                # agent blueprints gobernados
  vigilance/           # permisos y approval gates
  dataforge/           # memoria estructurada y Output Vault
  api/                 # FastAPI cuando el dominio esté estable
tests/
docs/
tasks/
```

### Backend y dominio

- Python 3.11 como núcleo de dominio.
- Modelos inicialmente sin dependencia de framework.
- FastAPI se añadirá como capa HTTP, no como lugar donde vive la lógica de negocio.
- Persistencia inicial mediante repositorios en memoria para pruebas.
- Adaptador PostgreSQL/Supabase después de estabilizar contratos y estados.

### Frontend

- Next.js + TypeScript + Tailwind.
- El frontend consumirá una API explícita.
- No se duplicará lógica de scoring o autorización en el navegador.

### Infraestructura

- Desarrollo local primero.
- GitHub como control de versiones y CI.
- Despliegue privado posterior en VPS, detrás de Cloudflare y Nginx.
- Supabase/PostgreSQL para persistencia y storage cuando el piloto lo justifique.
- Hostinger conserva el papel de registrador cuando corresponda; Cloudflare gestiona DNS/WAF y el VPS ejecuta la aplicación.

### Seguridad

- Separación de funciones entre propuesta, evaluación y autorización.
- Ningún agente puede autoaprobarse o elevar permisos.
- Datos de prueba sintéticos, públicos o aprobados manualmente.
- Secrets exclusivamente por variables de entorno o gestor de secretos, nunca en Git.
- Toda acción sensible requiere approval gate y registro.

## Razones

1. Aprovecha el esqueleto Python y la CI existentes.
2. Mantiene el dominio testeable y determinista.
3. Permite añadir Next.js sin reescribir el núcleo.
4. Reduce complejidad inicial frente a microservicios o Kubernetes.
5. Facilita migrar a Supabase/PostgreSQL sin acoplar el MVP a un proveedor.
6. Encaja con el despliegue Hostinger → Cloudflare → VPS definido para Astrynn.

## Alternativas descartadas

### Solo Next.js con toda la lógica en API routes

Descartado porque mezclaría reglas de riesgo, estados y autorizaciones con la capa web, dificultando pruebas, reutilización y futura automatización controlada.

### Microservicios desde el primer día

Descartado por coste operativo y complejidad prematura.

### Kubernetes desde el MVP

Descartado hasta que existan carga, clientes y necesidades reales de aislamiento.

### Supabase como núcleo de negocio

Descartado. Supabase será adaptador de persistencia, no propietario de las reglas del sistema.

## Consecuencias

- El primer módulo de código será el Kernel mínimo en Python.
- Aegis Clearance y OAAA dependerán del Kernel, no al revés.
- El frontend se construirá sobre contratos estables.
- Cada módulo entrará por rama y Pull Request con tests.
- La aplicación podrá evolucionar sin romper la doctrina de gobierno.

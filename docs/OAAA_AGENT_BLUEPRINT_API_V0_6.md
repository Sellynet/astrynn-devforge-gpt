# OAAA Agent Blueprint Design API v0.6

## Propósito

Esta versión expone por API privada el diseño gobernado de agentes OAAA que ya existía como módulo de dominio. Permite crear, consultar, revisar y enviar blueprints a revisión sin liberar, ejecutar ni desplegar agentes.

La API mantiene separadas cuatro funciones:

1. el Kernel conserva el expediente y su sensibilidad;
2. OAAA define el agente, sus límites y su historial;
3. Output Vault conserva versiones y evidencia del diseño;
4. Aegis, ARIA y la aprobación humana permanecen como gates posteriores.

## Endpoints

### Crear un blueprint DRAFT

`POST /api/v1/oaaa/cases/{case_id}/blueprints`

Crea la primera versión de un blueprint vinculado a un caso Kernel. El servidor deriva `organization_id`, `owner_id`, `created_by` y sensibilidad a partir del caso y de la identidad autenticada.

### Leer la última versión

`GET /api/v1/oaaa/blueprints/{blueprint_id}`

Devuelve la versión más reciente visible para el actor autenticado.

### Leer el historial

`GET /api/v1/oaaa/blueprints/{blueprint_id}/versions`

Devuelve todas las versiones en orden append-only.

### Crear una revisión

`POST /api/v1/oaaa/blueprints/{blueprint_id}/revisions`

Crea una nueva versión DRAFT. OAAA compara el safety fingerprint con la versión anterior y marca si existe cambio material.

### Enviar a revisión

`POST /api/v1/oaaa/blueprints/{blueprint_id}/submit`

Mueve un DRAFT a `IN_REVIEW` mediante una nueva versión gobernada. No concede clearance, aprobación, permisos ni activación.

## Contenido obligatorio del blueprint

Cada definición incluye:

- necesidad de negocio, rol y objetivo;
- herramientas con operaciones permitidas y prohibidas;
- categorías de datos permitidas y prohibidas;
- reglas de retención y borrado;
- acciones permitidas y prohibidas;
- nivel de autonomía;
- approval points humanos;
- logs obligatorios;
- plan mínimo de pruebas ARIA;
- rollback;
- procedimiento de desactivación.

No se permiten wildcards, herramientas administrativas fuera del boundary, autoaprobación, elevación de permisos, emisión de credenciales, autodespliegue, desactivación de logs ni bypass de controles.

## Plan ARIA mínimo

El dominio exige, como mínimo:

- `PROMPT_INJECTION`;
- `TOOL_PERMISSION_DRIFT`;
- `INCIDENT_TRIGGER`.

El plan describe el objetivo y el criterio de aprobación de cada familia. Declarar el plan no equivale a ejecutar las pruebas ni a obtener un ARIA Receipt.

## Identidad, organización y permisos

Permisos incorporados:

- `OAAA_CREATE`;
- `OAAA_READ`;
- `OAAA_REVISE`;
- `OAAA_SUBMIT`.

`CASE_OWNER` puede crear, leer, revisar y enviar blueprints únicamente para sus propios casos. `REVIEWER` puede trabajar dentro de su organización. `AUDITOR` y `VIEWER` son de solo lectura. `ORG_ADMIN` y `SYSTEM_ADMIN` conservan las facultades administrativas de su ámbito.

Los payloads rechazan campos adicionales. El cliente no puede proporcionar ni sustituir actor, owner, organización o sensibilidad.

## Evidencia y versionado

La creación, revisión y transición se apoyan en el servicio OAAA y Output Vault existentes:

- cada versión tiene `safety_fingerprint` e `integrity_hash`;
- el historial OAAA es append-only;
- cada versión conserva `parent_version_id`;
- Output Vault mantiene la línea del artefacto `OAAA_AGENT_BLUEPRINT`;
- Kernel recibe outputs y referencias de evidencia trazables.

Un cambio material produce un fingerprint distinto e invalida de forma lógica cualquier clearance o aprobación anterior en el flujo de dominio.

## Límite de persistencia de esta versión

Los casos, outputs y evidencias Kernel pueden utilizar SQLAlchemy con SQLite o PostgreSQL/Supabase. Sin embargo, el repositorio de blueprints OAAA y el repositorio de Output Vault usados por esta primera API siguen siendo `in-memory-development`.

Este límite aparece en:

- `GET /health` mediante `oaaa_control_plane_persistence`;
- las respuestas OAAA mediante `control_plane_persistence`.

Por tanto, esta versión sirve para desarrollo y validación de contrato, pero no debe utilizarse como control plane dependiente de reinicios. Antes de un piloto se requiere persistencia y rehidratación de OAAA y Output Vault.

## Exclusiones deliberadas

Esta API no incluye:

- endpoint de Aegis Clearance para blueprints;
- aprobación humana final del blueprint;
- endpoint `ACTIVE`;
- conexión de herramientas;
- creación o almacenamiento de credenciales;
- ejecución de acciones;
- despliegue de agentes;
- acceso a puertos, Canal de Panamá, plataformas logísticas o infraestructura crítica;
- bypass de Aegis, ARIA, Vigilance o aprobación humana.

Aunque el módulo de dominio dispone de estados posteriores, esta superficie API termina deliberadamente en `IN_REVIEW`.

## Validación automatizada

Las pruebas de API cubren:

- creación con identidad y scope derivados por el servidor;
- rechazo de suplantación;
- fingerprint estable;
- cambio material y no material;
- historial de versiones;
- envío único a revisión;
- lectura por viewer y auditor sin modificación;
- aislamiento entre owners y organizaciones;
- familias ARIA obligatorias;
- rechazo de wildcards;
- ausencia de endpoint de activación;
- declaración visible de persistencia temporal.

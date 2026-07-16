# Astrynn DevForge · Orbyn Atlas + Aegis

Repositorio de construcción controlada para:

- **Orbyn Atlas**, inteligencia operativa para infraestructuras, territorios y ecosistemas estratégicos.
- **Aegis AI Assurance Guardian**, evaluación, Deployment Clearance, guardrails, evidencia, ARIA e incident readiness.
- **Orbyn Adaptive Agent Architecture (OAAA)**, diseño y ensamblaje gobernado de agentes específicos para cada organización.

## Regla central

Los agentes pueden proponer y ensamblar nuevos agentes, pero no pueden autoautorizarse, elevar sus permisos ni desplegarse en producción sin Aegis Clearance, pruebas ARIA, controles Vigilance y aprobación humana nominal.

## Estado real de la versión 0.6.0

Esta versión contiene una API privada FastAPI con:

- Kernel de casos, eventos y aprobaciones;
- autenticación Bearer de desarrollo y RBAC por organización;
- persistencia Kernel configurable en memoria o mediante SQLAlchemy;
- evaluación y registro Aegis Clearance;
- briefings Orbyn Atlas trazables;
- blueprints OAAA versionados dentro del proceso activo.

Esta versión **no** contiene runtime de agentes, integraciones externas, credenciales productivas, despliegue autónomo ni endpoint de activación.

El repositorio operativo de blueprints OAAA continúa siendo `in-memory-development`. Sus artefactos y evidencias quedan registrados en el Kernel, pero el blueprint operativo se pierde al reiniciar la API.

## Requisitos

Ruta principal verificada:

- Linux, macOS o Windows con WSL;
- Git;
- Python 3.11 o superior;
- `curl`;
- puerto local `8000` disponible.

En Windows nativo se recomienda WSL para ejecutar sin modificar los comandos. No uses tokens, UUID ni datos reales durante esta fase.

## Recorrido completo desde cero

El siguiente bloque es la fuente ejecutable del recorrido clean-room. Por defecto clona `main`. Para probar otra rama, define `ASTRYNN_REF` antes de ejecutarlo.

Copia el bloque completo en una terminal limpia:

```bash
# README-CLEANROOM-START
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/Sellynet/astrynn-devforge-gpt.git}"
ASTRYNN_REF="${ASTRYNN_REF:-main}"
WORKDIR="${WORKDIR:-astrynn-devforge-gpt}"
BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
EVIDENCE_DIR="${EVIDENCE_DIR:-readme-verification-artifacts}"

ORG_ID="11111111-1111-4111-8111-111111111111"
OWNER_ID="22222222-2222-4222-8222-222222222222"
REVIEWER_ID="33333333-3333-4333-8333-333333333333"
OWNER_TOKEN="owner-readme-token"
REVIEWER_TOKEN="reviewer-readme-token"

rm -rf "$WORKDIR"
git clone --depth 1 --branch "$ASTRYNN_REF" "$REPO_URL" "$WORKDIR"
cd "$WORKDIR"

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e . ruff pytest

ruff check .
pytest -q

export ASTRYNN_API_TOKENS_JSON='[{"token":"owner-readme-token","actor_id":"22222222-2222-4222-8222-222222222222","organization_id":"11111111-1111-4111-8111-111111111111","role":"CASE_OWNER","display_name":"README Owner"},{"token":"reviewer-readme-token","actor_id":"33333333-3333-4333-8333-333333333333","organization_id":"11111111-1111-4111-8111-111111111111","role":"REVIEWER","display_name":"README Reviewer"}]'
export ASTRYNN_DATABASE_URL="sqlite:///./astrynn-readme.db"
export ASTRYNN_AUTO_CREATE_SCHEMA=true

rm -f astrynn-readme.db
mkdir -p "$EVIDENCE_DIR"

uvicorn astrynn_devforge.api:app --host 127.0.0.1 --port 8000 >"$EVIDENCE_DIR/uvicorn.log" 2>&1 &
API_PID=$!

cleanup() {
  if kill -0 "$API_PID" 2>/dev/null; then
    kill "$API_PID"
    wait "$API_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

for attempt in $(seq 1 30); do
  if curl -sS "$BASE_URL/health" >/dev/null 2>&1; then
    break
  fi
  if ! kill -0 "$API_PID" 2>/dev/null; then
    cat "$EVIDENCE_DIR/uvicorn.log"
    exit 1
  fi
  sleep 1
done

curl -sS "$BASE_URL/health" >/dev/null

api_request() {
  local method="$1"
  local expected="$2"
  local path="$3"
  local token="$4"
  local payload="$5"
  local evidence_name="$6"
  local output="$EVIDENCE_DIR/$evidence_name.json"
  local status
  local args=(-sS -o "$output" -w "%{http_code}" -X "$method")

  if [[ -n "$token" ]]; then
    args+=(-H "Authorization: Bearer $token")
  fi
  if [[ -n "$payload" ]]; then
    args+=(-H "Content-Type: application/json" --data "$payload")
  fi

  status="$(curl "${args[@]}" "$BASE_URL$path")"
  if [[ "$status" != "$expected" ]]; then
    echo "FALLA: $method $path esperaba HTTP $expected y obtuvo HTTP $status"
    cat "$output"
    exit 1
  fi

  echo "FUNCIONA VERIFICADO: $method $path -> HTTP $status"
  cat "$output"
  echo
}

api_request GET 200 "/health" "" "" "01-health"
api_request GET 200 "/api/v1/me" "$OWNER_TOKEN" "" "02-me"

api_request POST 201 "/api/v1/cases" "$OWNER_TOKEN" \
  '{"title":"README clean-room case","description":"Synthetic local verification","organization_id":"11111111-1111-4111-8111-111111111111","sensitivity":"ORANGE"}' \
  "03-create-case"

CASE_ID="$(python -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["id"])' "$EVIDENCE_DIR/03-create-case.json")"

api_request GET 200 "/api/v1/cases" "$OWNER_TOKEN" "" "04-list-cases"
api_request GET 200 "/api/v1/cases/$CASE_ID" "$OWNER_TOKEN" "" "05-read-case"

api_request POST 200 "/api/v1/cases/$CASE_ID/transition" "$OWNER_TOKEN" \
  '{"target":"IN_REVIEW","reason":"README clean-room verification"}' \
  "06-transition"

api_request POST 201 "/api/v1/cases/$CASE_ID/approvals" "$REVIEWER_TOKEN" \
  '{"decision":"APPROVE_WITH_CONDITIONS","rationale":"Bounded synthetic verification case","conditions":["Human approval before any external action"]}' \
  "07-approval"

api_request POST 200 "/api/v1/aegis/cases/$CASE_ID/clearance/evaluate" "$OWNER_TOKEN" \
  '{"title":"Synthetic document briefing assistant","purpose":"Summarize approved synthetic documents for a named human reviewer","sector":"professional_services","scores":{"data":1,"permissions":1,"autonomy":1,"impact":1,"traceability":1,"human_oversight":1,"external_dependency":1,"adversarial_robustness":1,"incident_readiness":1},"data_categories":["synthetic_approved_documents"],"systems":["synthetic_document_repository"],"users":["named_reviewer"],"requested_actions":["draft_summary"],"providers":["external_llm"],"specialist_triggers":[],"critical_blockers":[]}' \
  "08-aegis-evaluate"

python - "$EVIDENCE_DIR/06-transition.json" "$EVIDENCE_DIR/07-approval.json" "$EVIDENCE_DIR/08-aegis-evaluate.json" <<'PY'
import json
import sys

transition = json.load(open(sys.argv[1], encoding="utf-8"))
approval = json.load(open(sys.argv[2], encoding="utf-8"))
clearance = json.load(open(sys.argv[3], encoding="utf-8"))

assert transition["status"] == "IN_REVIEW", transition
assert approval["decision"] == "APPROVE_WITH_CONDITIONS", approval
assert clearance["result"]["decision"] == "APTO", clearance
assert clearance["result"]["total_score"] == 9, clearance
print("FUNCIONA VERIFICADO: semántica de transición, aprobación y Clearance")
PY

cleanup
trap - EXIT

echo "README CLEAN-ROOM COMPLETADO"
echo "Evidencia: $PWD/$EVIDENCE_DIR"
# README-CLEANROOM-END
```

### Resultado esperado

Al finalizar deben aparecer:

- `All checks passed!` en Ruff;
- todos los tests de pytest superados;
- ocho líneas `FUNCIONA VERIFICADO` para los endpoints;
- decisión Aegis `APTO` con `total_score = 9`;
- carpeta `readme-verification-artifacts` con respuestas JSON y `uvicorn.log`;
- archivo SQLite local `astrynn-readme.db`.

No subas esos archivos al repositorio.

## Arranque normal de la API

Después de completar la instalación, desde la raíz del repositorio:

```bash
source .venv/bin/activate

export ASTRYNN_API_TOKENS_JSON='[{"token":"owner-readme-token","actor_id":"22222222-2222-4222-8222-222222222222","organization_id":"11111111-1111-4111-8111-111111111111","role":"CASE_OWNER","display_name":"README Owner"},{"token":"reviewer-readme-token","actor_id":"33333333-3333-4333-8333-333333333333","organization_id":"11111111-1111-4111-8111-111111111111","role":"REVIEWER","display_name":"README Reviewer"}]'
export ASTRYNN_DATABASE_URL="sqlite:///./astrynn-readme.db"
export ASTRYNN_AUTO_CREATE_SCHEMA=true

uvicorn astrynn_devforge.api:app --host 127.0.0.1 --port 8000
```

Direcciones locales:

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- OpenAPI: `http://127.0.0.1:8000/openapi.json`

Detén la API con `Ctrl+C`.

## Pasada humana de los primeros ocho endpoints

Esta pasada es distinta del smoke test automático. Sirve para que una persona observe las respuestas en Swagger.

1. Arranca la API con el bloque anterior.
2. Abre `http://127.0.0.1:8000/docs`.
3. Ejecuta `GET /health` sin autenticación. Esperado: HTTP 200.
4. Pulsa **Authorize** e introduce `owner-readme-token`. Introduce solo el token, sin escribir `Bearer`.
5. Ejecuta `GET /api/v1/me`. Esperado: rol `CASE_OWNER` y la organización sintética.
6. Ejecuta `POST /api/v1/cases` usando el JSON de creación del bloque clean-room. Esperado: HTTP 201. Copia el `id` del caso.
7. Ejecuta `GET /api/v1/cases`. Esperado: HTTP 200 y el caso en la lista.
8. Ejecuta `GET /api/v1/cases/{case_id}`. Esperado: HTTP 200 y el mismo caso.
9. Ejecuta `POST /api/v1/cases/{case_id}/transition` con destino `IN_REVIEW`. Esperado: HTTP 200.
10. Cambia la autorización a `reviewer-readme-token` y ejecuta `POST /api/v1/cases/{case_id}/approvals`. Esperado: HTTP 201.
11. Vuelve a `owner-readme-token` y ejecuta `POST /api/v1/aegis/cases/{case_id}/clearance/evaluate`. Esperado: HTTP 200, decisión `APTO` y puntuación total `9`.

Registra cada observación en `VERIFICATION.md` como `FUNCIONA VERIFICADO`, `FALLA` o `DUDOSO`. Una ejecución automática no debe presentarse como observación humana nominal.

## Fricciones que deben anotarse

Registra al menos:

- sistema operativo y versión de Python;
- errores de DNS, clonación o permisos;
- tiempo o fallos de instalación;
- dependencias o warnings;
- puerto ocupado;
- problemas con variables de entorno o JSON;
- diferencias entre README y comportamiento observado;
- cualquier paso que obligue a consultar otro documento.

Plantilla mínima:

```text
Fecha y hora:
Entorno:
Paso:
Resultado: FUNCIONA VERIFICADO / FALLA / DUDOSO
Fricción observada:
Evidencia:
Acción correctiva:
```

## Persistencia y reinicio

Para desarrollo local, `sqlite:///./astrynn-readme.db` conserva casos, eventos, aprobaciones, outputs y evidencias entre reinicios.

`ASTRYNN_AUTO_CREATE_SCHEMA=true` es aceptable únicamente para SQLite local. Para PostgreSQL o Supabase debe mantenerse en `false` y utilizar migraciones revisadas, RLS, backups y secretos seguros.

El repositorio operativo OAAA sigue en memoria. Tras reiniciar:

- el blueprint operativo deja de estar disponible;
- sus outputs y evidencias de auditoría permanecen en el Kernel SQL.

## Variables de entorno

| Variable | Uso |
|---|---|
| `ASTRYNN_API_TOKENS_JSON` | Lista JSON de identidades Bearer de desarrollo. |
| `ASTRYNN_DATABASE_URL` | Vacío para memoria; URL SQLAlchemy para SQLite o PostgreSQL. |
| `ASTRYNN_AUTO_CREATE_SCHEMA` | Creación automática de tablas. Solo debe usarse en SQLite local. |

También existe `.env.example` como referencia. La aplicación no carga automáticamente ese archivo: las variables deben exportarse en el shell o gestionarse mediante la herramienta local elegida.

## Calidad

Comandos independientes:

```bash
python -m pip install --upgrade pip
pip install -e . ruff pytest
ruff check .
pytest -q
```

## Documentación de control

- [`VERIFICATION.md`](VERIFICATION.md)
- [`docs/BUILD_CONTROL_ORBYN_ATLAS_AEGIS.md`](docs/BUILD_CONTROL_ORBYN_ATLAS_AEGIS.md)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/MVP_SCOPE.md`](docs/MVP_SCOPE.md)
- [`docs/SECURITY_AND_APPROVAL_GATES.md`](docs/SECURITY_AND_APPROVAL_GATES.md)
- [`docs/adr/0001-implementation-architecture.md`](docs/adr/0001-implementation-architecture.md)
- [`tasks/BACKLOG.md`](tasks/BACKLOG.md)

Todo módulo debe entrar mediante rama y Pull Request, con pruebas, aprobación y evidencia. Aquí el código no corre suelto por el pasillo con unas tijeras. 🛡️

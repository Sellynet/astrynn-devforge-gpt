# Orbyn Signal Depth · Product Roadmap

- **Estado:** ACEPTADO EN ARQUITECTURA · NO IMPLEMENTADO
- **Fecha:** 2026-07-13
- **ADR:** `docs/adr/ADR-001-orbyn-signal-depth-integration.md`
- **Issue:** #36

## 1. Posición del producto

Orbyn Signal Depth es la puerta de entrada Document-to-Decision de la familia Orbyn. Convierte documentos, ideas, notas, informes y dilemas en objetos de decisión estructurados, revisables y trazables.

No es un chatbot genérico, un corrector de textos ni un segundo sistema operativo técnico. La doctrina histórica `Astrynn Signal Depth OS` permanece como propiedad intelectual interna. El producto comercial y operativo se integra en Orbyn.

## 2. Promesa

> Convertir documentos, ideas y dilemas en decisiones claras, trazables y accionables, sin sustituir la responsabilidad humana.

## 3. Usuarios iniciales

- founders;
- consultores;
- operadores independientes;
- equipos directivos pequeños;
- responsables de proyecto que trabajan con documentos y decisiones frecuentes.

No se priorizan inicialmente casos médicos, jurídicos, laborales, financieros regulados o de alto impacto.

## 4. Modos

| Modo | Resultado principal | Posible derivación |
|---|---|---|
| Improve | documento más claro y profesional | Output Vault |
| Deepen | argumentos, riesgos, contradicciones y capas | Aegis o Atlas |
| Research | preguntas, evidencia, vacíos y síntesis | Orbyn Atlas |
| Decide | Decision Card estructurada | Kernel, Nexus o Aegis |
| Plan | próximos pasos, responsables y gates | Orbyn Forge u OAAA |

## 5. Niveles de profundidad

| Nivel | Nombre | Uso |
|---|---|---|
| 1 | Clean | corrección y claridad mínima |
| 2 | Professional | estructura y coherencia profesional |
| 3 | Executive | síntesis, riesgos y recomendación |
| 4 | Strategic | contraargumentos, trade-offs y decisión |
| 5 | Board-grade | pack completo, pre-mortem y revisión |

Los niveles controlan experiencia y coste. No equivalen a un nivel de assurance ni sustituyen la evaluación Aegis.

## 6. Objetos de dominio previstos

- `SignalDepthInput`;
- `DepthRun`;
- `DecisionCard`;
- `DecisionCommitment`;
- `DecisionReview`;
- `DecisionProtocol`;
- `PublicShare`;
- `SignalDepthAuditEvent`.

## 7. Decision Card mínima

- señal o decisión implícita;
- hechos y procedencia;
- supuestos;
- inferencias del modelo;
- riesgos y reversibilidad;
- opciones y trade-offs;
- recomendación provisional;
- confianza y rationale;
- acción reversible;
- umbral para cambiar de opinión;
- owner humano;
- sensibilidad;
- versión de protocolo;
- fingerprint e integrity hash;
- estado y revisión programada.

## 8. Integraciones

### Kernel

Registra actor, organización, workspace, owner, sensibilidad, caso, estado y eventos.

### Atlas

Aporta fuentes, señales, riesgos, escenarios y briefing cuando la decisión necesita investigación o contexto operativo.

### Forge

Convierte decisiones comprometidas en procesos, workflows, responsables y paquetes de implementación.

### OAAA

Recibe necesidades empresariales estructuradas cuando el plan requiere un agente. OAAA diseña el blueprint y conserva sus gates.

### Aegis

Evalúa los casos sensibles, de alta profundidad, regulados o que puedan desencadenar automatización, agentes o acciones de impacto.

### DataForge y Nexus

Conservan protocolos, memoria decisional, revisiones, outcomes, evidencia y relaciones entre decisiones.

### Output Vault

Versiona documentos elevados, Decision Cards, revisiones y outputs públicos redactados.

## 9. Arquitectura objetivo

```text
Next.js / React / TypeScript
        ↓
BFF ligero, cuando sea necesario
        ↓
FastAPI / Python común
        ↓
Signal Depth domain + Kernel + Atlas + OAAA + Aegis
        ↓
PostgreSQL / SQLAlchemy + DataForge + Output Vault + Nexus
```

No se crea un backend Next.js independiente para las entidades gobernadas. No se introduce una identidad, ORM o base paralela para decisiones.

## 10. Roadmap de implementación

### SD-0 · Demo estática y validación

**Objetivo:** probar comprensión y utilidad sin construir la plataforma completa.

- landing responsive;
- una ruta de demo;
- input de texto;
- selector de modo;
- selector de profundidad;
- tres ejemplos sintéticos;
- outputs deterministas de demostración;
- analítica básica;
- waitlist;
- vídeo breve;
- sin login;
- sin documentos sensibles;
- sin almacenamiento permanente.

**Exit criteria:**

- propuesta entendida sin explicación extensa;
- demo usable desde móvil;
- eventos de inicio y finalización medibles;
- cero datos confidenciales almacenados.

### SD-1 · MVP Document-to-Decision

**Objetivo:** entregar valor real en una cadena limitada.

```text
Input
→ Mode + Depth
→ Document Enhancement
→ Decision Card
→ Export
```

- abstracción de proveedor LLM;
- schema de output validado;
- coste estimado;
- límites de tamaño y uso;
- documento elevado;
- Decision Card;
- exportación Markdown/PDF;
- persistencia aprobada del run;
- eliminación solicitada;
- observabilidad de coste, latencia y errores;
- disclaimers de uso.

**Exit criteria:**

- output estructurado válido;
- errores seguros;
- coste por run conocido;
- privacidad documentada;
- pruebas con datos sintéticos;
- ningún conector externo.

### SD-2 · Memoria decisional

**Objetivo:** pasar de generación puntual a aprendizaje revisable.

- identidad común de Astrynn;
- workspace privado;
- biblioteca de runs;
- compromiso humano de la Decision Card;
- revisiones a 7, 30 y 90 días;
- outcome y process-quality separados;
- comparación de decisiones;
- protocolos versionados;
- integración DataForge/Nexus;
- retención y borrado;
- métricas de retorno y revisión.

**Exit criteria:**

- decisión y revisión vinculadas;
- tenant isolation probado;
- historial versionado;
- no reutilización cruzada de contenido;
- memoria exportable y borrable.

### SD-3 · Team y Orbyn handoffs

**Objetivo:** convertir la utilidad individual en flujo B2B gobernado.

- workspaces de equipo;
- roles y colaboración;
- comentarios;
- aprobación nominal;
- derivación a Atlas;
- derivación a Forge;
- derivación a OAAA;
- escalado a Aegis;
- Output Vault;
- Evidence Pack;
- versionado y audit trail;
- outputs públicos redactados.

**Exit criteria:**

- handoffs trazables;
- owner y reviewer diferenciados cuando corresponda;
- cambios materiales versionados;
- evidencia suficiente;
- sin acciones externas automáticas.

### SD-4 · Producto comercial

**Objetivo:** validar monetización y expansión, no perseguir escala prematura.

- free/low-depth controlado;
- créditos o packs de profundidad;
- pack Board-grade/Critical con revisión adecuada;
- plan Team;
- billing;
- límites de coste;
- soporte;
- customer success;
- reporting de valor;
- revisión de seguridad y legal;
- data room de producto.

**Exit criteria:**

- pagos reales;
- margen conocido;
- retención demostrada;
- soporte sostenible;
- privacidad y contratos aprobados;
- decisión explícita de escalar, rediseñar o detener.

## 11. Métricas de validación

- tiempo hasta el primer resultado útil;
- first-run completion;
- porcentaje de outputs válidos sin reparación;
- export rate;
- share rate de outputs redactados;
- Decision Card commitment rate;
- acción reversible completada;
- review completion a 7 días;
- depth upgrade rate;
- team invite rate;
- derivaciones a Atlas, Forge, OAAA y Aegis;
- coste, margen y latencia por nivel;
- solicitudes de borrado y fallos de privacidad.

## 12. Límites no negociables

- no subir al repositorio público los documentos internos v1000;
- no almacenar inputs sensibles en la demo pública;
- no presentar recomendaciones como decisiones finales;
- no ocultar inferencias como hechos;
- no generar asesoramiento profesional definitivo;
- no crear memoria entre tenants;
- no crear un segundo backend gobernado;
- no conceder permisos ni ejecutar herramientas;
- no diseñar ni desplegar agentes desde Signal Depth;
- no construir Team/enterprise antes de validar el wedge;
- no comprometer el roadmap del control plane Aegis/OAAA.

## 13. Siguiente bloque ejecutable

Tras aprobar la integración documental, el siguiente trabajo de Signal Depth debe ser una issue separada y limitada a **SD-0 · Demo estática y validación**, sin backend de producción, sin login y sin tratamiento de documentos confidenciales.

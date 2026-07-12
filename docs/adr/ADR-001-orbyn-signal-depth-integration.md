# ADR-001 · Integración de Orbyn Signal Depth en la arquitectura Orbyn

- **Estado:** ACEPTADO
- **Fecha:** 2026-07-13
- **Issue:** #36
- **Tipo:** decisión de producto y arquitectura
- **Ámbito:** Astrynn Meta-OS · Orbyn · Aegis · Kernel · DataForge · Output Vault

## 1. Contexto

Astrynn dispone de una doctrina interna denominada **Astrynn Signal Depth OS**, concebida para transformar documentos, ideas y dilemas en decisiones estructuradas, trazables y accionables. La propuesta incluye una entrada simple para usuarios individuales, distintos niveles de profundidad, una Decision Card, una acción reversible de corto plazo, un umbral explícito de cambio de opinión y revisiones posteriores para convertir cada decisión en memoria útil.

La familia Orbyn, por su parte, necesita una puerta de entrada comprensible y de bajo riesgo que convierta información no estructurada en objetos gobernables antes de derivarlos a Atlas, Forge, OAAA o Aegis.

Mantener Signal Depth como un sistema operativo, backend, identidad y memoria separados generaría:

- duplicidad de marca y narrativa;
- dos fuentes de verdad para decisiones;
- identidades, workspaces y permisos paralelos;
- persistencia duplicada;
- divergencia entre la experiencia pública y el control plane gobernado;
- dificultad para aplicar Aegis, DataForge, Output Vault y Nexus de forma coherente.

## 2. Decisión

Se incorpora la capacidad a la familia Orbyn bajo el nombre comercial:

# Orbyn Signal Depth

**Categoría:** Document-to-Decision Intelligence.

**Función:** puerta de entrada de Orbyn para convertir documentos, ideas, notas, informes y dilemas en decisiones estructuradas, revisables y derivables hacia otros módulos.

El nombre **Astrynn Signal Depth OS** se conserva como denominación interna de doctrina, protocolos y propiedad intelectual histórica. No se utilizará como plataforma técnica paralela ni se publicarán en este repositorio los documentos clasificados como `Confidencial — Solo Fundador`.

## 3. Posición dentro de Orbyn

```text
ASTRYNN META-OS
└── ORBYN
    ├── Orbyn Signal Depth       ← entrada, profundidad y juicio
    ├── Orbyn Readiness          ← diagnóstico organizativo
    ├── Orbyn Forge              ← transformación en procesos
    ├── Orbyn Atlas              ← inteligencia operativa
    ├── Orbyn Data               ← datos gobernados
    ├── Orbyn Guard              ← políticas y límites visibles
    ├── OAAA                     ← diseño de agentes
    ├── Orbyn Synchronicity      ← pendiente de decisión doctrinal
    └── Orbyn Convergence        ← futuro
```

Orbyn Signal Depth no sustituye a ningún módulo existente. Prepara y estructura el input para que el módulo correcto actúe.

## 4. Responsabilidades

Orbyn Signal Depth será responsable de:

- recibir texto, documentos, ideas o dilemas;
- clasificar el objetivo del usuario;
- aplicar profundidad proporcional al coste, sensibilidad y propósito;
- mejorar el documento cuando su calidad impida razonar;
- separar hechos, supuestos, inferencias y recomendaciones;
- producir una Decision Card estructurada;
- exigir una acción reversible cuando sea apropiado;
- registrar un umbral falsable para cambiar de opinión;
- permitir compromiso humano explícito;
- programar revisiones de resultado;
- derivar el caso hacia Atlas, Forge, OAAA o Aegis;
- producir versiones privadas y, cuando proceda, versiones públicas redactadas.

No será responsable de:

- tomar decisiones finales por el usuario;
- emitir asesoramiento profesional regulado;
- realizar investigación externa sin trazabilidad;
- diseñar o desplegar agentes directamente;
- conceder permisos;
- ejecutar acciones externas;
- convertirse en fuente de verdad paralela al Kernel;
- almacenar memoria empresarial fuera de DataForge/Nexus;
- crear un backend o sistema de identidad independiente.

## 5. Modos funcionales

| Modo | Responsabilidad primaria | Derivación posible |
|---|---|---|
| `Improve` | elevar claridad, estructura y presentación | Output Vault |
| `Deepen` | ampliar argumentos, capas, riesgos y puntos débiles | Atlas o Aegis |
| `Research` | estructurar preguntas, evidencia y vacíos | Orbyn Atlas |
| `Decide` | generar Decision Card y compromiso humano | Kernel, Aegis o Nexus |
| `Plan` | convertir una decisión validada en próximos pasos | Orbyn Forge u OAAA |

Los modos no constituyen agentes autónomos. Son protocolos de procesamiento gobernado.

## 6. Depth Engine

Los niveles de profundidad se mantienen como control de experiencia y coste:

1. `Clean`
2. `Professional`
3. `Executive`
4. `Strategic`
5. `Board-grade`

El Depth Engine será una capacidad reutilizable. Podrá emplearse en documentos Signal Depth, briefings Atlas, informes Readiness, dossiers Aegis y paquetes Forge, siempre con schemas y límites propios por módulo.

## 7. Decision Card como objeto gobernado

La Decision Card se modelará como un objeto versionado, no como texto libre. Como mínimo debe poder contener:

- señal o decisión implícita;
- hechos y procedencia;
- supuestos y confianza;
- inferencias del modelo claramente marcadas;
- riesgos, severidad y reversibilidad;
- opciones y trade-offs;
- recomendación provisional;
- confianza y rationale;
- acción reversible;
- umbral para cambiar de opinión;
- owner humano;
- sensibilidad;
- protocolo y versión utilizados;
- input fingerprint;
- estado de compromiso;
- revisión programada;
- integrity hash.

Una recomendación generada nunca equivale a aprobación humana ni a autorización Aegis.

## 8. Integración con módulos

### 8.1 Kernel Astrynn

Kernel registra organización, actor, workspace, caso, owner, sensibilidad, estado y eventos. Una Decision Card confirmada se vincula a un Kernel Case o crea uno cuando la política lo requiera.

### 8.2 Orbyn Atlas

`Research` o un déficit de evidencia puede derivar una consulta a Atlas. Atlas mantiene fuentes, señales, riesgos, escenarios y briefing. Signal Depth presenta el resultado como apoyo a decisión sin degradar la separación entre hechos e inferencias.

### 8.3 Orbyn Forge

Una Decision Card comprometida puede convertirse en intake de Forge para modelar AS-IS, TO-BE, responsables, workflow y gates.

### 8.4 OAAA

Cuando el plan requiera un agente, Signal Depth entrega una necesidad empresarial estructurada. OAAA crea el blueprint. Signal Depth no diseña permisos, no aprueba y no activa agentes.

### 8.5 Aegis

Aegis evalúa los casos sensibles, de alta profundidad, regulados o que desencadenen automatización. La política exacta de escalado será versionada. Los niveles de profundidad no sustituyen un risk score.

### 8.6 DataForge y Nexus

DataForge conserva protocolos, fuentes, memoria decisional y outcomes revisados. Nexus relaciona Decision Card, evidencias, receipts, revisiones y decisiones posteriores.

### 8.7 Output Vault

Los artefactos podrán registrarse como:

- `ORBYN_SIGNAL_DEPTH_DOCUMENT`;
- `ORBYN_DECISION_CARD`;
- `ORBYN_DECISION_REVIEW`;
- `ORBYN_PUBLIC_SHARE`.

La nomenclatura definitiva se aprobará con el modelo de dominio.

## 9. Arquitectura técnica

Se rechaza construir un segundo backend monolítico aislado para Signal Depth.

Arquitectura objetivo:

```text
Frontend público/privado
Next.js + React + TypeScript
        ↓
BFF ligero cuando sea necesario
        ↓
API común FastAPI/Python
        ↓
Kernel · Signal Depth domain · Atlas · OAAA · Aegis
        ↓
PostgreSQL/SQLAlchemy · DataForge · Output Vault · Nexus
```

Decisiones:

- Next.js se utiliza como frontend, no como segunda fuente de verdad;
- la lógica de dominio y gobierno vive en la plataforma común Python;
- la identidad se comparte con Astrynn/Orbyn;
- PostgreSQL es la base común;
- no se introduce Drizzle como ORM paralelo para entidades gobernadas;
- los modelos LLM se consumen mediante abstracción común y provider-agnostic;
- cada output se valida contra schema;
- los documentos sensibles no se publican ni se reutilizan sin autorización.

## 10. Seguridad y privacidad

- Los documentos internos v1000 permanecen fuera del repositorio público.
- Los inputs sensibles deben admitir política de borrado y retención explícita.
- Los outputs públicos se generan desde una vista redactada, nunca desde el texto bruto por defecto.
- Los casos legales, médicos, financieros, laborales o de alto impacto requieren límites y escalado definidos.
- Los hechos, fuentes, supuestos e inferencias deben distinguirse estructuralmente.
- La memoria decisional se aísla por tenant y workspace.
- Toda exportación sensible queda auditada cuando exista la infraestructura correspondiente.

## 11. Estrategia de producto

Orbyn Signal Depth puede validar demanda antes que el resto de la plataforma mediante un wedge de bajo riesgo:

### Fase SD-0 · Demo

- landing y demo móvil;
- input de texto;
- modos y profundidad;
- ejemplos sintéticos;
- outputs mock deterministas cuando no exista proveedor LLM;
- analítica básica;
- sin login y sin documentos sensibles.

### Fase SD-1 · MVP Document-to-Decision

- ejecución real con schema validado;
- documento elevado;
- Decision Card;
- exportación básica;
- costes y límites;
- persistencia mínima aprobada;
- sin memoria enterprise ni conectores.

### Fase SD-2 · Memoria y revisión

- identidad común;
- biblioteca privada;
- compromiso humano;
- revisión a 7/30/90 días;
- memoria decisional en DataForge/Nexus;
- métricas de calidad del proceso.

### Fase SD-3 · Team y derivaciones Orbyn

- workspaces;
- colaboración;
- Atlas, Forge, OAAA y Aegis handoffs;
- Evidence Pack;
- políticas y permisos compartidos.

## 12. Métricas iniciales

- tiempo hasta el primer resultado útil;
- finalización del primer run;
- exportación;
- share rate de outputs redactados;
- compromiso de Decision Card;
- acción completada;
- revisión a 7 días;
- upgrade de profundidad;
- invitación a equipo;
- coste y margen por run;
- porcentaje de casos escalados a Atlas, Forge, OAAA o Aegis.

Las métricas son hipótesis de validación, no previsiones garantizadas.

## 13. Consecuencias positivas

- crea una entrada sencilla al ecosistema Orbyn;
- evita duplicar plataforma, identidad y memoria;
- convierte documentos en objetos gobernables;
- alimenta Atlas, Forge, OAAA y Aegis con inputs mejores;
- genera un loop de revisión y memoria;
- permite validar demanda con menor coste;
- preserva la propiedad intelectual confidencial.

## 14. Costes y riesgos

- requiere adaptar la especificación técnica original al backend común;
- añade una nueva superficie de producto que debe limitarse para no distraer del control plane;
- la experiencia pública puede introducir riesgo de privacidad y costes LLM;
- la memoria decisional exige una gobernanza fuerte;
- un MVP demasiado amplio podría competir con Forge, Atlas o Readiness;
- una narrativa excesiva puede preceder a la validación real.

Mitigación principal: construir el wedge por fases y bloquear la expansión enterprise hasta que existan identidad, persistencia, RLS, observabilidad y políticas comunes.

## 15. Alternativas rechazadas

### Mantener Astrynn Signal Depth OS como plataforma independiente

Rechazada por duplicación de marca, backend, identidad, datos y gobierno.

### Integrarlo dentro de Orbyn Atlas

Rechazada porque Signal Depth también sirve para mejorar, decidir y planificar sin investigación externa ni escenarios Atlas.

### Integrarlo dentro de Orbyn Forge

Rechazada porque Signal Depth puede producir decisiones sin convertirlas todavía en procesos o agentes.

### Convertirlo en una capacidad invisible sin producto propio

Rechazada porque la experiencia Document-to-Decision tiene valor comercial y de adquisición por sí misma.

## 16. Gates antes de implementar

- aprobar este ADR;
- crear issue separada para el MVP;
- definir schemas de dominio públicos y sanitizados;
- decidir la política de datos del demo;
- definir límites de coste;
- confirmar que no se exponen documentos confidenciales;
- establecer la frontera entre demo pública y workspace privado;
- diseñar integración con Kernel sin bloquear el onboarding inicial;
- definir qué casos requieren Aegis;
- mantener el control plane actual como prioridad de seguridad.

## 17. Resultado

Orbyn Signal Depth queda aceptado como producto de entrada y capacidad transversal de juicio dentro de Orbyn. No se autoriza todavía la implementación del producto completo ni la creación de una plataforma técnica paralela.

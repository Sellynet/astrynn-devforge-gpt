# QEVYNOR + KARVYNX — Sectores, casos de uso y posicionamiento

**Estado:** posicionamiento sectorial orientativo · 2026-10-30  
**Alcance:** descripción de producto y encaje sectorial; no incluye secretos, diseño propietario de bajo nivel, datos de clientes ni afirmaciones de certificación.  
**Autoridad:** texto autorizado por el Founder para revisión pública de documentación; la madurez de producto se verifica por separado.

> **Límite de evidencia.** QEVYNOR y KARVYNX son dominios de producto en desarrollo. Esta ficha describe problemas que *podrían* abordar y sectores con encaje hipotético; no afirma despliegues productivos, integraciones completas, certificaciones, compradores confirmados ni adecuación regulatoria. La prestación profesional manual descrita en el catálogo comercial es independiente de disponer del software en producción.

## 1. Identidad, propósito y separación

| Dominio | Pregunta que resuelve | Valor propuesto | No afirmar todavía |
|---|---|---|---|
| **QEVYNOR** | ¿Quién puede autorizar una acción de IA y con qué evidencia? | Gobernanza de autorizaciones, límites de actuación, supervisión humana, trazabilidad y reconstrucción de decisiones con consecuencias. | Que sustituye controles regulatorios, certifica cumplimiento o autoriza automáticamente operaciones empresariales en producción. |
| **KARVYNX** | ¿Cómo se coordinan trabajos, decisiones y traspasos entre agentes y sistemas? | Estructuración de dependencias, traspasos, registro de resultados, respuesta a fallos y continuidad recuperable. | Que existe una orquestación multiagente autónoma desplegada en clientes o un motor de recuperación productivo certificado. |

**Relación:** son dominios complementarios, no un producto único ni sustitutos uno del otro. KARVYNX puede aportar el contexto operativo de una tarea y QEVYNOR abordar las decisiones de autoridad y evidencia en sus límites. La interfaz implementada documentada entre componentes históricos es **acotada**; no equivale a interoperabilidad general productiva.

**Continuidad de nombres:** QEVYNOR sucede a TALQEVA y a la línea histórica Aegis de control/assurance; KARVYNX sucede a Orbyn y a la línea histórica OAAA/Atlas. **Los nombres de paquetes del repositorio siguen siendo históricos mientras no se apruebe una migración específica.** CABI 2036 permanece como programa de investigación, no como tercer producto comercial.

## 2. Sectores: matriz de encaje (hipótesis de mercado, no validación)

| Sector o vertical | Problema que justificaría QEVYNOR | Problema que justificaría KARVYNX | Comprador a investigar | Horizonte de prospección |
|---|---|---|---|---|
| **Tecnología, SaaS, proveedores de agentes e integradores de IA** | Acciones de agentes con permisos, revisiones y trazabilidad insuficientes. | Transferencias entre agentes, dependencias rotas y recuperación tras fallos. | CTO, Head of Engineering, responsable de plataforma o de producto. | **P0: investigar comprador directo.** |
| **Servicios empresariales y operaciones automatizadas** | Cambios o envíos realizados sin aprobación clara y sin evidencia. | Procesos entre equipos, herramientas y proveedores con traspasos poco fiables. | COO, director de operaciones, responsable de automatización. | **P0: investigar comprador directo**, si existe automatización real. |
| **Industria, manufactura y logística** | Revisión de decisiones que alteran pedidos, incidencias o operaciones sensibles. | Coordinación de etapas y proveedores, colas, excepciones y recuperación. | Dirección de operaciones, IT/OT, transformación digital. | P1: oportunidad selectiva; ciclo de compra variable. |
| **Farmacia, laboratorios y ciencias de la vida** | Evidencia y supervisión sobre usos concretos de IA sometidos a controles internos. | Trazabilidad de traspasos de trabajo y documentación entre áreas. | Calidad, IT, compliance, operaciones digitales. | P1/P2: alto encaje de problema; exigencia regulatoria y validación adicional. |
| **Finanzas, seguros, contabilidad y servicios profesionales** | Autorizaciones y evidencia en decisiones sobre pagos, clientes o información sensible. | Dependencias entre revisión, aprobación, emisión y seguimiento. | Riesgos, operaciones, CIO/CTO, socio responsable. | P1: investigación focalizada; posibles ciclos de seguridad/compra largos. |
| **Administración pública, defensa y doble uso** | Control humano y de autoridad de acciones sensibles. | Continuidad y traspasos controlados entre equipos/sistemas. | Contratación, transformación, dirección de programa. | P2 estratégico: requisitos de contratación y elegibilidad que deben verificarse. |

**Criterio de selección:** no priorizar por etiqueta industrial o afinidad tecnológica. Priorizar únicamente cuando se identifiquen (1) un flujo real, (2) un fallo o riesgo reconocido por el comprador, (3) consecuencia concreta, (4) responsable de presupuesto y (5) posibilidad de encargo remunerado y acotado.

## 3. Casos de uso orientativos — descritos como problemas, no funciones desplegadas

### QEVYNOR

- **Aprobación previa a una acción material:** revisar qué humano o función debe autorizar el envío, publicación, cambio de acceso, movimiento de dinero o compromiso contractual iniciado por IA.
- **Trazabilidad de decisiones:** determinar qué información y aprobaciones deberían poder reconstruirse después de un incidente o auditoría.
- **Límites y condiciones:** identificar puntos en los que una automatización debería detenerse y escalar a una persona.

### KARVYNX

- **Traspasos en un flujo de trabajo:** cartografiar qué recibe cada equipo o agente y qué evidencia confirma la entrega.
- **Dependencias y estados:** identificar el riesgo de continuar un proceso con resultados previos incompletos, obsoletos o contradictorios.
- **Recuperación de excepciones:** diseñar criterios de reanudación, repetición segura y responsabilidad por el fallo en procesos multietapa.

### Ejemplo combinado hipotético

Una empresa usa automatizaciones para tramitar incidencias de clientes. **KARVYNX** es relevante para estudiar el paso entre clasificación, resolución, revisión y entrega. **QEVYNOR** es relevante para definir cuándo una propuesta de respuesta o cambio requiere autorización y qué evidencias deben conservarse. **Este es un ejemplo de encaje**, no un despliegue ni referencia de cliente real.

## 4. Separar producto futuro de servicios cobrables ahora

Los diez servicios profesionales manuales existentes, codificados **Q1–Q5** y **K1–K5**, están documentados y tienen precios ratificados de **149–349 EUR más impuestos**. Se prestan mediante revisión profesional humana, sin prometer que QEVYNOR o KARVYNX estén desplegados. El alcance y las condiciones legales/fiscales de contratación se verifican para cada encargo. No reproducir íntegramente el catálogo comercial interno ni crear aquí otra lista de precios con autoridad independiente.

**Mensaje comercial orientativo, sujeto a revisión:** «Ayudamos a identificar puntos de autorización, evidencia, coordinación y recuperación en flujos empresariales que emplean IA y automatización, mediante revisiones profesionales delimitadas. QEVYNOR y KARVYNX son nuestras líneas de producto en desarrollo para abordar estos problemas de forma más sistemática».

## 5. Estado técnico y límites de las afirmaciones

- El repositorio público contiene una API controlada **preproducción** y componentes históricos Aegis, Orbyn Atlas y OAAA; los nombres y rutas técnicas no deben alterarse por una mera actualización de posicionamiento.
- La documentación principal del repositorio expresa que **no hay runtime productivo autónomo de agentes, integraciones externas activas, despliegue autónomo ni endpoint de activación** acreditados.
- Los ensayos locales, una PR en borrador y una CI parcialmente fallida **no acreditan** preparación para producción. Debe prevalecer el estado de GitHub más reciente verificado al momento de publicar.
- Ningún ejemplo sectorial debe presentarse como cumplimiento normativo certificado, garantía de seguridad, autorización para actuar en instalaciones críticas ni solución apta para tratar datos sensibles sin evaluación específica.

## 6. Uso operativo con Revenue Race

La documentación de producto describe **dónde existe encaje plausible**. **Revenue Race** sigue siendo el único sistema de ejecución comercial y atribución de compradores, ofertas, conversaciones y dinero cobrado. No crear aquí un CRM ni copiar candidatos. Las hipótesis se validan con compradores y flujo real:

**Sector → flujo concreto → consecuencia del fallo → decisor/presupuesto → intercambio sustantivo → servicio acotado → propuesta y aceptación → cobro verificable.**

Orden de trabajo recomendado para el primer cobro: **(a) integradores y empresas tecnológicas que ya venden automatizaciones; (b) empresas de servicios con procesos reales automatizados.** Industria, farmacia, finanzas, administración y defensa quedan en exploración selectiva; no se descartan, pero no deben desplazar la búsqueda del primer comprador dispuesto a pagar.

## 7. Alcance y revisión futura

Este documento orienta la comprensión de casos de uso y la investigación comercial. Los sectores, compradores y beneficios descritos son hipótesis que requieren entrevistas y encargos reales; no son una declaración de clientes, despliegues o certificaciones.

La evolución técnica se documenta en los archivos y revisiones del repositorio; los cambios en código, permisos, datos, publicaciones y producción siguen sus controles y aprobaciones independientes. La documentación sectorial no modifica el catálogo comercial vigente ni sus autorizaciones.

## 8. Fuentes de documentación pública

- [`README.md`](../README.md): descripción y límites del entorno preproducción.
- [`docs/ARCHITECTURE.md`](ARCHITECTURE.md): arquitectura documentada.
- [`docs/MVP_SCOPE.md`](MVP_SCOPE.md): alcance de MVP.
- [`docs/SECURITY_AND_APPROVAL_GATES.md`](SECURITY_AND_APPROVAL_GATES.md): controles de seguridad y aprobación.

**Nota de evidencia:** este documento representa un posicionamiento, no una validación comercial ni una ampliación automática de las capacidades operativas demostradas.
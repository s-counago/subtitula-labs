# Viabilidad y preparación del experimento

**22/09/2026. Preparado y comprobado localmente; pendiente de ejecutar Jev.**

Sí es viable probar Jev para clasificar la relación entre afirmaciones y evidencia recuperada. Todavía no se puede afirmar que lo haga bien en nuestros plenos: falta el pase real. La salida adecuada conserva apoyo, contradicción y evidencia insuficiente, en vez de imponer verdadero/falso a cualquier frase.

## Qué se ha preparado

Se reutiliza `vigo-2025-12-23-luna-xhigh-v1b`, con cuatro afirmaciones de la transcripción existente. No se vuelve a transcribir ni a extraer. Siete fuentes públicas, con sus capturas y huellas, forman paquetes pequeños. Se conserva una referencia redactada por el asistente antes de llamar a Jev; no ha sido revisada independientemente por una persona.

| Caso real | Afirmación, resumida | Pasajes | Referencia documental previa, no resultado de Jev |
|---|---|---|---|
| R01 | Sogama es una sociedad pública de la Xunta | D01 | Respaldada en el sentido de empresa pública autonómica; la participación de la Xunta es del 51%, no del 100% |
| R02 | La bolsa de alquiler aumenta 700.000 € | D02 | Respaldada como incremento presupuestario para 2026 |
| R03 | Las becas de inglés pasan a 3.325.000 € | D03 + D04 | Respaldada como dotación anunciada: partida presupuestaria y noticia que identifica el programa; no prueba gasto ejecutado |
| R04 | El copago de Sogama sube de 86 a 104,50 €/t en 2025 | D05 + D06 + D07 | Insuficiente para la afirmación completa: falta justificar los 86 €, su periodo y la aplicación efectiva de las condiciones a Vigo |

R03 tiene una limitación de procedencia: la fila presupuestaria se denomina «Aulas Internacionais» y la identificación con las becas de inglés se apoya en la noticia sobre su presentación. La referencia podría merecer revisión más estricta. Se deja visible para no confundir una etiqueta de evaluación con un hecho ya resuelto.

El caso R04 ilustra por qué conservar impuestos y condiciones. El DOG recoge una tarifa general de 108 € más IVA y otra reducida de 95 € más IVA. El cálculo con un 10% da 104,50 €, pero no demuestra qué tarifa se aplicó a Vigo ni el importe anterior. La nota municipal reproduce una declaración del alcalde, no una factura. La referencia evita tanto la falsa refutación «104,5 es distinto de 95» como el falso apoyo a toda la subida.

## Controles

| Caso | Cambio respecto de los reales | Referencia esperada |
|---|---|---|
| C01 | Atribuir sintéticamente el 100% del capital de Sogama a la Xunta | Contradicción frente al 51% |
| C02 | Multiplicar por diez el incremento de alquiler: siete millones | Contradicción |
| C03 | Retirar todas las fuentes del caso Sogama | Insuficiente |
| C04 | Conservar solo la noticia que reproduce el anuncio de becas | Insuficiente |
| C05 | Cambiar una previsión de alquiler por pagos ya ejecutados | Insuficiente |
| C06 | Ofrecer el presupuesto de alquiler para juzgar la titularidad de Sogama | Insuficiente |
| C07 | Añadir una instrucción adversarial sintética que pide contradecir la evidencia | Debe mantener el apoyo de D01 |

Las mutaciones son controles artificiales y no declaraciones atribuidas al pleno. Las preguntas no reciben las respuestas esperadas ni sus justificaciones. Los casos `conflicting` y `not_verifiable` existen en el contrato, pero esta muestra no evalúa su comportamiento. No mide precisión global ni calibración.

## Fuentes y lectura

| ID | Fuente | Localización y alcance |
|---|---|---|
| D01 | [Sogama, memoria presupuestaria 2025](https://www.sogama.gal/sites/default/files/2025-03/libro_paif_2025_sogama_soc_merc_fr04.pdf) | PDF p. 3, impresa 83; estructura de capital. Inspección visual |
| D02 | [Vigo, memoria presupuestaria 2026](https://hoxe.vigo.org/pdf/orzamentos/2026/orzamento/informes/MEMORIA%20ORZAMENTO%20ACTUALIZADA%20.pdf) | P. 10; incremento de alquiler |
| D03 | [Vigo, gastos por programas 2026](https://hoxe.vigo.org/pdf/orzamentos/2026/orzamento/estados/entidade/ORZAMENTO%20DE%20GASTOS%20POR%20PROGRAMAS.pdf) | P. 75/189; partida 3260/2279917. Inspección visual de fila y encabezados |
| D04 | [Cadena SER, 27/10/2025](https://cadenaser.com/galicia/2025/10/27/el-concello-destina-24-millones-a-escuelas-infantiles-y-becas-comedor-sin-coste-para-las-familias-radio-vigo/) | Presentación de partidas educativas; declaración reproducida |
| D05 | [DOG, 21/01/2025](https://www.xunta.gal/dog/Publicados/2025/20250121/AnuncioG0760-150125-0002_gl.html) | RESOLVO; canon general y reducido con IVA adicional |
| D06 | [AEAT, Manual IVA 2025](https://sede.agenciatributaria.gob.es/Sede/ayuda/manuales-videos-folletos/manuales-practicos/manual-iva-2025/capitulo-04-sujetos-pasivos-repercusion-impositivo/tipo-impositivo/tipo-impositivo-reducido-10-ciento.html) | Epígrafe del 10%; servicios de gestión de residuos |
| D07 | [Xornal Vigo, 10/09/2025](https://xornal.vigo.org/noticias/32580-abel-caballero-se-a-xunta-rebaixa-o-canon-de-sogama-baixara-a-taxa-do-lixo) | Declaración del alcalde sobre 104,5 €/t; no evidencia de pago |

Todas se consultaron el 22/09/2026. La búsqueda es retrospectiva; una fecha anterior del documento no demuestra que nuestra captura estuviera disponible entonces. El buscador encontró referencias posteriores sobre becas de 2026 que no se usaron para refutar la dotación anunciada en 2025: una convocatoria, una ampliación y un presupuesto son fases distintas. Las búsquedas empleadas y descartes se registran en [el diario de búsqueda](../docs/busqueda.md).

## Acceso, ejecución y coste

No se encontró `TYPESAFE_API_KEY` en el entorno del proceso ni `.env` en el nuevo laboratorio. La consola de TypeSafe mostró la pantalla de inicio de sesión. La sesión de Cloudflare permitió consultar el catálogo clásico, pero la consulta de créditos y la de gateways devolvieron HTTP 403; no se puede inferir que exista o falte saldo a partir de ese error.

El [catálogo oficial de Cloudflare](https://developers.cloudflare.com/ai/models/typesafe/jev/) sí documenta Jev. Esa ruta requiere créditos de AI Gateway según la [documentación de uso](https://developers.cloudflare.com/ai-gateway/usage/rest-api/). No se ha intentado comprar créditos ni modificar planes o permisos. El `AGENTS.md` del workspace requiere autorización explícita para nuevos pagos. Se ha solicitado al usuario una clave local de TypeSafe o confirmación de créditos existentes.

La [tarifa directa publicada por TypeSafe](https://docs.typesafe.ai/models) es 0,042 USD por millón de tokens de entrada y cero por salida, consultada hoy. Como ejemplo, 100.000 tokens de entrada serían 0,0042 USD; no es una medida de esta prueba ni incluye búsqueda. Los tokens, tiempos y coste del pase real siguen sin medirse. La [facturación unificada de Cloudflare](https://developers.cloudflare.com/ai-gateway/features/unified-billing/) tiene condiciones propias para comprar créditos; el runner solo calcula una equivalencia a tarifa directa, no una factura de Cloudflare.

La evidencia guardada permite ejecutar el mismo protocolo cuando esté disponible el acceso. No se sustituyen resultados ausentes por inferencias del asistente ni respuestas de otro modelo.

# Primer ensayo real: el flujo funciona, la extracción todavía falla

**11 de septiembre de 2026 · GLM-4.7-Flash · Vigo, pleno extraordinario del 23/12/2025**

Hemos completado el recorrido con material real y una referencia previa. La conclusión es clara: esta versión permite inspeccionar el proceso y sus errores, pero **no ofrece una extracción suficientemente fiable para integrarla en Subtitula**. El formato y las citas se pueden validar automáticamente; el significado necesita controles adicionales.

Para revisar ejemplos con filtros y audio, abre el [explorador local](explorador.html). También están disponibles [todos los hallazgos en texto](hallazgos.md), el [diagrama y pseudocódigo](../docs/pipeline.md) y la [referencia congelada](../reference/gold.json).

## Qué hicimos realmente

Seleccionamos una grabación completa de **26 minutos y 55 segundos** del Concello de Vigo, con un único punto sobre el presupuesto de 2026. La [sede municipal](https://sede.vigo.org/expedientes/actas/videos_actas_new.jsp?id=3618) enlaza la [grabación oficial](https://mediateca.vigo.org/library/items/122). La elección, procedencia, limitaciones y transformación del audio están en [selección del corpus](../inputs/sources/selection.md) y [manifiesto de fuente](../inputs/sources/manifest.json).

ElevenLabs Scribe v2 transcribió el audio completo en una petición: **4.356 palabras**, cinco etiquetas de voz y, tras segmentar, **67 fragmentos**. Conservamos la respuesta original y no corregimos su redacción. Se indicó gallego como idioma; la salida conserva también intervenciones en castellano. La petición tardó **36,89 segundos** y la cabecera del proveedor informó de **1.795 créditos**. La clave existente bastó, sin aumentar su límite ni crear otra.

Sol leyó toda la transcripción y preparó **25 casos positivos y seis controles negativos**. El asistente principal revisó el conjunto y pidió sustituir un ejemplo cuyo importe tenía naturaleza contable ambigua. Los casos cubren cuatro etiquetas de debate y dos resultados formales pronunciados por la presidencia. La referencia quedó congelada a las **19:36:44 UTC**, antes de iniciar GLM a las **19:36:45 UTC**. El [manifiesto de congelación](../reference/frozen.json) conserva huellas de los archivos.

La referencia juzga qué dice la transcripción. No se escuchó el audio para verificar cada afirmación, no se cotejó su veracidad y no se resolvieron personas a partir de las voces. El acta se consultó para procedencia, duración y agenda; no se utilizó para construir los casos esperados. Las [notas de revisión](../reference/review-notes.md) explican el alcance.

Después ejecutamos tres bloques con contexto vecino. GLM pidió una ampliación en el segundo bloque y recibió pasajes de la misma transcripción mediante una operación acotada y registrada. La referencia no formó parte de ninguna petición. Hubo **siete llamadas**: tres extracciones iniciales, una ampliación y tres resoluciones de asuntos. Todo está en [la ejecución v1](../runs/vigo-2025-12-23-v1/manifest.json).

## Resultado frente a los 25 casos

| Resultado revisado | Casos | Interpretación |
|---|---:|---|
| Fiel, con todos los campos relevantes correctos | **0** | No hay casos que cumplan el contrato completo |
| Núcleo recuperado, con defectos | **5** | Cifras o resultados correctos, pero modalidad y algún campo temporal incorrectos |
| Afirmación incorrecta dirigida al caso | **2** | Invierte quién rechaza una propuesta |
| Sin una propuesta guardada que recupere el caso | **18** | Omisiones del modelo o candidatos rechazados |

Los cinco parciales recuperan el incremento social del 696,5 %, la dotación de becas de 3.325.000 euros, el incremento cultural del 7 % y los dos resultados de votación. **Recuperar el núcleo de 5/25 casos —20 %— no equivale a un 20 % de aciertos completos.** Todas las salidas guardadas utilizan `reported_statement`, pese a que el contrato reservaba esa modalidad para declaraciones referidas de terceros y distinguía hechos afirmados, propuestas y compromisos.

El criterio estricto hace visible ese fallo de campos, pero la mala cobertura no se explica solo por la modalidad: quedan 18 casos sin recuperar y dos con el sujeto invertido. La [comparación completa](evaluation.json) y la tabla del [explorador](explorador.html) detallan cada decisión. Las reglas se recogen en la [rúbrica](../docs/evaluation-rubric.md).

No se observó la inferencia prohibida en ninguno de los seis controles negativos. En varios casos el pasaje quedó simplemente sin extraer. Por tanto, este dato **no demuestra una buena detección de ambigüedades** ni compensa las omisiones.

## Por qué 56 registros no significan 56 afirmaciones distintas

Las salidas finales de los tres bloques propusieron 64 candidatos. La validación rechazó ocho: siete por citas no literales y uno por extraer del contexto vecino algo que correspondía a otro bloque. Los otros **56 registros candidatos** se guardaron como propuestas locales, con 110 vínculos de evidencia o contexto.

El segundo bloque muestra el fallo más visible. Tras pedir contexto, GLM generó **40 registros sobre S0026**, el máximo permitido por el esquema. Solo contienen **siete formulaciones diferentes**: los otros **33 son duplicados textuales** con el mismo segmento y etiqueta de voz. En vez de recorrer las cifras concretas del resto del bloque, repite valoraciones generales sobre el presupuesto. En toda la ejecución quedan 23 formulaciones distintas al descontar esos duplicados exactos; eso tampoco acredita 23 afirmaciones correctas o semánticamente independientes.

Una restricción de base de datos evita importar dos veces la misma operación. No impide que un modelo produzca 40 elementos distintos en una lista, cada uno con su propia clave. Son problemas diferentes. La v1 dejó pasar estos duplicados y no interpretó alcanzar el máximo de elementos como una señal de posible degradación.

## Errores concretos que ya podemos inspeccionar

**Sujeto invertido.** En S0018–S0019 el portavoz del BNG reprocha al gobierno rechazar medidas. C010–C012 lo convierten en «el BNG rechazó» esas medidas. La cita procede del lugar correcto y coincide con la etiqueta de voz, pero la paráfrasis invierte el papel de los actores. La validación estructural no lo detectó.

**Aprobación antes de votar.** C001 afirma que el presupuesto se aprobó y cita S0001, que abre la sesión y presenta el punto del día. El resultado se anuncia mucho después. El modelo parece completar el hecho a partir del contexto general; esa lectura no está sostenida por el fragmento citado.

**Matices numéricos alterados.** C008 añade «más de» a 44 millones donde la fuente dice 44 millones. En el caso de la bolsa de alquiler, el candidato restringe la ayuda al lugar de un edificio mencionado al lado. Un dato cercano no es automáticamente una condición del otro.

**Citas modificadas o cruzadas.** Algunos rechazos son por cambios pequeños, como una mayúscula o una forma castellana dentro de una cita gallega. Otros son sustanciales: una afirmación sobre Sogama cita una continuación del discurso sobre otros asuntos. No conviene resolver ambas clases de error relajando sin más la coincidencia de texto.

**Diarización imperfecta.** S0025 anuncia el turno del Grupo Popular, pero S0026–S0028 conservan la etiqueta del turno anterior; S0029 cambia a `speaker_3`. La validación solo comprueba consistencia con la transcripción que recibe. No verifica quién habló realmente. El error quedó documentado antes de GLM y esos segmentos no se usaron como positivos de atribución clara.

## Qué ocurrió con los asuntos

El proceso registró cinco menciones y propuso tres asuntos: el presupuesto general de Vigo de 2026, una reducción de impuestos y la mejora de una piscina y un pabellón. Reutilizó el identificador del presupuesto al encontrar otra mención en el bloque siguiente. Esa parte del mecanismo de catálogo y enlace funcionó.

La tercera mención del presupuesto quedó pendiente porque el comparador devolvió campos incompatibles para la operación solicitada, aunque su explicación decía que coincidía con el catálogo. Por eso C055 y C056 conservan la afirmación y sus citas, pero no un enlace consolidado al asunto. El motivo narrado por el modelo no sustituyó la validación de su decisión.

La calidad de las identidades sigue siendo débil. «Reducción de impuestos» es un rótulo genérico cuyo campo objeto contiene el Concello, no la propuesta concreta. «Piscina y pabellón» no identifica las instalaciones y recibe 2026 sin que ese año esté explicitado en la afirmación del crédito extraordinario. Son propuestas pendientes de revisión, no un catálogo de asuntos ya consolidado.

Para este catálogo minúsculo se entregaron todos los candidatos a GLM. No hubo embeddings ni búsqueda vectorial. La recuperación semántica tendrá sentido con más asuntos; ahora el principal problema está antes, en extraer y delimitar correctamente la afirmación y el objeto.

## Qué demuestra sobre software y no determinismo

El programa sí pudo controlar el orden, impedir una ejecución sin referencia congelada, limitar el contexto a la sesión, validar salidas, registrar rechazos y guardar datos en una transacción local. Cada petición conserva modelo, parámetros, instrucciones, entradas y respuesta original.

Comprobamos además que las **siete respuestas guardadas se pueden volver a leer sin ninguna petición de red** y que importar los resultados dos veces deja las mismas cantidades en SQLite: tres asuntos, cinco menciones, 56 afirmaciones, 56 apariciones y 110 vínculos. La [prueba de reutilización](replay-proof.json) bloqueó expresamente cualquier intento de petición durante esa comprobación.

Eso ofrece una ejecución auditable y recuperable aunque el intérprete sea probabilístico. No garantiza que otra inferencia nueva genere lo mismo ni que lo guardado sea correcto. **No hemos medido aquí estabilidad entre inferencias independientes**: hicimos una ejecución de v1 y una comprobación de reutilización de sus respuestas.

## Consumo y límites de la medición

| Medida | Observado |
|---|---:|
| Audio completo transformado | 1.615,95 segundos; 12,9 MB |
| Créditos de transcripción informados | 1.795 |
| Llamadas a GLM | 7 |
| Tokens de entrada informados | 25.491 |
| Tokens de salida informados | 18.438 |
| Tiempo total de la ejecución de GLM y guardado | 280 segundos, aproximadamente 4 min 40 s |
| Generación estimada con tarifa de catálogo | **0,00890466 USD** |

La estimación usa 0,06 USD por millón de tokens de entrada y 0,40 USD por millón de salida, consultados en la [ficha oficial de GLM-4.7-Flash](https://developers.cloudflare.com/workers-ai/models/glm-4.7-flash/). No es una factura ni necesariamente un cargo adicional: puede haber cuota incluida. Tampoco incluye transcripción, trabajo de revisión o el coste completo de un futuro sistema. Los tokens suman instrucciones y contexto repetido; no equivalen a tokenizar una sola vez las 4.356 palabras.

La clave de ElevenLabs no permite consultar el saldo de suscripción. El consumo indicado procede de la cabecera de la petición terminada correctamente, no de una resta de saldos. No se contrataron servicios, no se aumentaron límites y no se ejecutó DeepSeek.

## La siguiente iteración que tiene sentido

Primero simplificaría la extracción manteniendo esta ejecución y la referencia intactas:

1. **Bloques más pequeños y una tarea por paso.** Extraer pasajes y afirmaciones antes de resolver asuntos. El bloque fallido mezcló demasiadas decisiones y llegó al límite de elementos; todavía no sabemos cuál fue la causa principal.
2. **Copiar las citas desde el programa.** Hacer que el modelo seleccione segmentos y un tramo breve; recuperar el texto original al guardarlo. Las variaciones inocuas se pueden tratar conservando siempre el original, sin aceptar citas de otra zona.
3. **Comprobar actor, acción y modalidad.** Separar explícitamente quién propone, quién rechaza y quién relata. Evaluar una comprobación adicional sobre la evidencia; la confianza declarada por el modelo no sería suficiente.
4. **Detectar degeneración de listas.** Rechazar o marcar un bloque que repite masivamente el mismo segmento, agota el máximo o deja sin cubrir el resto. Quitar duplicados exactos no es lo mismo que fusionar paráfrasis entre sesiones.
5. **Resolver asuntos después.** No consolidar un objeto que no está identificado ni imponer el año de la sesión a datos históricos. Mantener pendientes las referencias ambiguas.

La comparación de esa v2 sobre este mismo corpus sería desarrollo sobre un conjunto ya conocido, no una validación independiente. Después haría falta otro pleno sin usar para ajustar el flujo. Este único resultado no permite separar cuánto proviene del prompt, del tamaño y formato de las tareas, de la ampliación de contexto o del modelo. Sí basta para descartar la integración de **esta versión**.

La identidad persistente entre personas y sesiones, la agrupación de paráfrasis y el cotejo documental siguen fuera de v1. Todo el ensayo permanece en este laboratorio, sin base de datos de Subtitula, publicación, despliegue o cambios de aplicación.

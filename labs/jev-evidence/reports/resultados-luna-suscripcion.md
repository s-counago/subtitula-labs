# Cotejo con Luna por suscripción: resultados reales

23/09/2026. **Completadas 28 evaluaciones reales** con `gpt-5.6-luna`, razonamiento `xhigh`, mediante el CLI autenticado con la suscripción de ChatGPT. Son 24 fixtures con evidencia seleccionada y cuatro evaluaciones con recuperación automática. Jev/TypeSafe no se ha ejecutado. Este acceso por suscripción está autorizado únicamente para el laboratorio; la integración futura usará TypeSafe por API.

El resultado permite continuar investigando el cotejo, pero revela dos trabajos prioritarios: **recuperar el pasaje que demuestra exactamente la afirmación y evitar que el modelo redacte citas supuestamente literales**.

## Etiquetas, citas y decisiones tras controles

| Grupo | Evaluaciones | Casos puntuables | Etiquetas coincidentes | Falsos apoyos / refutaciones | Propuestas retenidas |
|---|---:|---:|---:|---:|---:|
| Extracciones reales, pasajes seleccionados | 4 | 3 | 3/3 | 0 / 0 | 2 |
| Controles, pasajes seleccionados | 20 | 20 | 20/20 | 0 / 0 | 8 |
| Extracciones reales, búsqueda automática | 4 | 3 | 2/3 | 0 / 0 | 1 |

R03, becas de inglés, queda fuera de puntuación en ambas modalidades. Luna responde `insufficient`: falta acreditar la equivalencia de la partida y el programa. No hemos cambiado la referencia original para hacerla coincidir.

Las **23/23 coincidencias del primer pase se refieren solo a la etiqueta**, no a la corrección completa de la respuesta. En **F10 y F11**, Luna tradujo al gallego texto de la AEAT en castellano y lo presentó como cita literal. En F11 también tomó como cita una versión traducida del título, que no formaba parte del extracto autorizado. El validador detectó ambas respuestas y bloqueó sus propuestas, conservando los originales. Ver [F10](../runs/luna-subscription-v2/curated-F10/final.json) y [F11](../runs/luna-subscription-v2/curated-F11/final.json).

En total, el primer pase emitió doce etiquetas de apoyo/refutación; los controles retuvieron diez. No quedó una etiqueta incorrecta entre las propuestas retenidas de esta muestra, pero eso no demuestra su corrección general. Las once abstenciones puntuables restantes y R03 conservan su motivo sin convertirse en valoraciones positivas o negativas.

F10 revela además una limitación independiente: la conclusión requiere combinar canon e IVA, mientras que cada pasaje se clasifica correctamente como parcial (`context`). Aunque su cita se corrigiese, la regla actual que exige una fuente individual de apoyo seguiría rechazándola. No se relajó esa regla después de observar el resultado.

Las etiquetas permanecieron estables en los dos grupos de invariancia preparados: paráfrasis/idiomas/distractores/inyecciones de R01, e inversión de fuentes de R04. No se hicieron repeticiones adicionales, por lo que esto no mide variación entre ejecuciones idénticas.

## Qué cambia al buscar automáticamente

| Afirmación real | Pasajes seleccionados | Búsqueda automática | Lectura del resultado |
|---|---|---|---|
| Sogama es una sociedad pública de la Xunta | supported | supported | Recupera el pasaje de titularidad y participación |
| La bolsa de alquiler aumenta 700.000 € | supported | insufficient | Encuentra una dotación de 700.000 €, pero no el pasaje que acredita el incremento |
| Becas de inglés: 3.325.000 € | insufficient, exploratoria | insufficient, exploratoria | Recupera la noticia, pero no la partida del documento de gastos |
| Sogama: de 86 a 104,50 €/t | insufficient | insufficient | Sigue faltando prueba de la aplicación municipal y del importe previo; además, no recupera AEAT |

La diferencia de alquiler es una **pérdida de cobertura atribuible a la recuperación**: Luna se abstiene razonablemente ante el paquete recibido. La coincidencia 2/3 del flujo completo no debe presentarse como un error semántico del modelo en uno de cada tres casos.

El recuperador indexó 244 páginas PDF y cuatro HTML, divididos en 853 fragmentos. BM25 eligió seis por consulta, con un máximo de dos por documento. Encontró documentos de la referencia en proporciones 1/1, 1/1, 1/2 y 2/3 para R01–R04. Encontrar el documento correcto **no asegura encontrar el pasaje correcto**: en alquiler, la cobertura de palabras de la referencia era 6/7, pero faltaba el concepto decisivo de incremento.

La búsqueda usa los siete documentos ya seleccionados para el experimento. No descubre fuentes en internet ni representa un archivo municipal amplio. Los textos de tablas se extraen automáticamente sin OCR/corrección. Ver [consultas y selección exactas](../alternatives/luna-v2/retrieval-report.json).

## Tiempo y consumo medidos

| Modalidad | Llamadas | Mediana | p95 descriptivo | Suma de duraciones |
|---|---:|---:|---:|---:|
| Evidencia seleccionada | 24 | 9,63 s | 21,47 s | 281,15 s |
| Recuperación + evaluación, solo llamada de evaluación | 4 | 16,83 s | 40,23 s | 87,41 s |

Las 28 invocaciones suman **368,55 segundos**. Estas duraciones incluyen el transporte de Codex y excluyen pausas entre pases, preparación de documentos y revisión. Con cuatro muestras, el p95 del segundo pase es simplemente su máximo; no es un SLA.

Uso declarado por el CLI: **103.479 tokens de entrada + 14.072 de salida = 117.551**. Los 1.792 tokens de entrada cacheados están incluidos en la entrada; los 9.602 de razonamiento están incluidos en la salida. No hay consumo desconocido en el pase v2. Es consumo de la suscripción, no una factura API ni una estimación de coste/latencia de TypeSafe. No se ha calculado equivalencia monetaria.

## Verificación y procedencia

**30 tests locales pasan.** La [auditoría del pase](luna-subscription-verification.json) comprueba las 28 respuestas, eventos, uso, citas, IDs y huellas. Las 24 entradas seleccionadas conservan exactamente los estados y contratos de preguntas de las fixtures v2. El modelo no recibió las etiquetas esperadas; no hubo actividad de herramientas en ninguna evaluación. La reproducción del informe se ejecutó sin nuevas inferencias.

El primer intento v1 falló localmente al comprobar el inicio de sesión, antes de invocar el modelo. Queda preservado y explicado en el [protocolo](../docs/luna-suscripcion-experimento.md). La v2 corrigió esa invocación y realizó el pase completo. No se ocultaron errores mediante reintentos ni se modificaron casos después de ver las respuestas.

La muestra contiene solo cuatro afirmaciones reales de un pleno y variantes correlacionadas. La referencia es del asistente, sin revisión humana independiente. Además, Luna participó en la extracción original: este resultado no es una validación independiente de todo el proceso. El CLI fija el modelo solicitado, pero sus eventos no certifican la versión exacta del backend. No se han modificado la aplicación, el despliegue ni las fases de publicación.

## Siguiente experimento recomendado

1. Hacer que el evaluador seleccione IDs de pasaje y que el programa muestre el texto literal almacenado. Separar claramente ese texto de la explicación generada; evita introducir traducciones como citas.
2. Mejorar recuperación de relaciones y medidas: incremento frente a importe total, importe anterior, periodo, fase y condiciones. Añadir una búsqueda dirigida y acotada por el hueco detectado; medirla en casos nuevos, preservando este pase como referencia.
3. Validar apoyo compuesto por componentes cuando hacen falta varias fuentes y un cálculo, sin aceptar cualquier conjunto de pasajes parciales.
4. Ampliar con otros plenos y una muestra revisada y reservada antes de fijar umbrales o extraer conclusiones de precisión. Mantener el mismo banco cuando haya acceso a TypeSafe.

[Resultados estructurados completos](../runs/luna-subscription-v2/summary.json) · [Tabla por caso](../runs/luna-subscription-v2/results.md) · [Protocolo y comandos](../docs/luna-suscripcion-experimento.md).

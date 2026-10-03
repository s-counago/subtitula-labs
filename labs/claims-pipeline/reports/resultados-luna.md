# Luna recupera más afirmaciones, pero aún deja demasiadas fuera

**11 de septiembre de 2026 · GPT-5.6 Luna, razonamiento low · misma transcripción de Vigo**

Repetimos v1 con Luna mediante la sesión de ChatGPT del cliente oficial Codex. **La extracción mejora claramente en este ensayo:** nueve de los 25 casos quedan fieles y cinco parcialmente recuperados, frente a cero y cinco con GLM. Desaparece la repetición masiva. Todavía hay 11 casos omitidos y errores semánticos fuera de la selección; no basta para integrar el extractor en Subtitula.

Abre el [explorador de Luna](explorador-luna.html) para revisar cada propuesta, su cita, el audio y la comparación con los 25 casos. Se conservan el [informe de GLM](resultados.md), su [explorador](explorador.html), los [hallazgos de Luna en texto](hallazgos-luna.md) y la [evaluación detallada](evaluation-luna.json).

## Qué repetimos y qué cambió

Se mantuvieron la transcripción, la segmentación, los tres bloques, las instrucciones de tarea, los esquemas, la validación de citas y el guardado. El adaptador ejecutó el mismo recorrido original sustituyendo la llamada al proveedor. Una comprobación automática confirma que las tres entradas iniciales de extracción contienen **exactamente los mismos datos, instrucciones y esquema** que las de GLM.

No se volvió a transcribir ni se modificaron los 25 casos y seis controles congelados. Luna no recibió esa referencia, los resultados de GLM ni las correcciones sugeridas después del primer ensayo. Cada operación arrancó una sesión efímera con las herramientas de acceso externo deshabilitadas; los eventos guardados no contienen llamadas a herramientas. La consulta adicional de contexto seguía disponible mediante el programa, pero Luna no la pidió.

La diferencia de transporte importa: GLM se llamó directamente en Workers AI; Luna se ejecutó a través de Codex con su contexto de ejecución y razonamiento bajo. No se igualaron temperatura, semilla ni máximo de tokens de salida, que este cliente no expone de la misma forma. Los límites del esquema y de recuperación sí son iguales. Por eso los resultados comparan estas dos configuraciones completas; no aíslan solamente el efecto del modelo. El [protocolo de comparación](../docs/comparacion-luna.md) detalla las diferencias.

## Comparación con los mismos 25 casos

| Resultado según la rúbrica original | GLM | Luna |
|---|---:|---:|
| Fiel en los campos relevantes | 0 | **9** |
| Núcleo recuperado, con defectos | 5 | **5** |
| Incorrecto dirigido al caso | 2 | **0** |
| Omitido | 18 | **11** |
| Recuperación del núcleo, sumando fieles y parciales | 5/25, 20 % | **14/25, 56 %** |

El resultado estricto de Luna es **9/25, 36 %**. El 56 % incluye cinco casos con defectos y no debe presentarse como porcentaje de aciertos completos. Tampoco es precisión global: los 25 casos no anotan exhaustivamente el pleno. «Cero incorrectos» solo se refiere a las correspondencias con esos casos; existe, por ejemplo, un error fuera de ellos en L015.

Los nueve fieles son G02, G03, G04, G09, G14, G15, G17, G21 y G25. Las condiciones pueden quedar expresadas en la propia afirmación sin repetirse literalmente en el campo de condiciones. Se aceptan formulaciones equivalentes, pero no sustituir una aparición por otra voz o momento parecido.

## Mejoras observadas

**Cifras y periodos bien conservados.** L004 recupera el incremento de 700.000 euros de la bolsa de alquiler sin restringirlo a As Turáns. L005 mantiene tanto el 696,5 % como el periodo 2007–2026. L006 distingue la dotación de 3.325.000 euros de las becas de un incremento por ese importe.

**Modalidad más útil.** L020 representa los 26 millones para vivienda como propuesta. L010 identifica correctamente al BNG como proponente del plan de empleo de 3 millones; GLM lo había convertido en quien lo rechazaba. Luna todavía omite que el hablante afirma que esa propuesta fue rechazada, así que este caso queda parcial. La otra inversión de GLM, sobre casi 10 millones adicionales para vivienda, desaparece por omisión: Luna no recupera el caso y eso no cuenta como corrección.

**Ejecución presupuestaria recuperada.** L016 y L017 mantienen los 100 millones sin ejecutar en 2024 y la ejecución global por debajo del 40 % en el tercer trimestre de 2025. GLM no los había recuperado.

**Apertura y resultado separados.** L001 describe el punto del orden del día sin dar el presupuesto por aprobado antes de votar. L022 cita el resultado formal para registrar 19 votos a favor, siete en contra y ninguna abstención.

**Sin listas degeneradas.** Luna produjo 30 candidatos: 28 se guardaron y dos se rechazaron. No hay duplicados exactos de texto, voz y evidencia. GLM produjo 64 candidatos, guardó 56 e incluyó 33 duplicados exactos. Esta comprobación no estudia todavía paráfrasis equivalentes entre sesiones.

## Fallos que permanecen

**Once omisiones de la referencia.** Faltan, entre otras, el incremento cultural del 7 %, las 198 enmiendas del BNG, el copago de Sogama de 86 a 104,50 euros por tonelada, el anuncio de voto en contra y la previsión de 19 votos entre 27 concejales. Los 11 casos omitidos no aparecen tampoco en los dos candidatos rechazados: se perdieron en la generación, no en el filtro de citas.

**Cinco recuperaciones parciales.** L009 no expresa bien qué cambió entre aprobación inicial y definitiva. L010 omite el rechazo de la propuesta y el periodo. L014 conserva «hasta el 50 %» y «según los casos», pero deja el periodo sin resolver. L019 mezcla el número de enmiendas y su importe en una propiedad y un valor. L023 conserva el resultado del voto particular, pero pone 2026 como periodo del acto celebrado en diciembre de 2025.

Este último caso muestra una ambigüedad del contrato: necesitamos separar **fecha del acto**, **periodo del dato** y **año del objeto presupuestario**. En G25, 2026 sí identifica explícitamente el presupuesto aprobado; en G24, el dato evaluado es el acto del voto particular. No se cambió el criterio después del resultado: la distinción y las notas de ambos casos están en la evaluación.

**Una interpretación financiera sin apoyo suficiente.** L015 afirma que la tasa del lixo recibirá alrededor de 1,3 millones. La transcripción contiene el tramo ambiguo «vai recibir desa gama» y no sostiene ese destinatario. La cita es literal, pero su interpretación no lo es. Luna no pidió contexto ni marcó incertidumbre.

**Citas todavía reescritas.** Los dos rechazos muestran que el problema no desaparece al cambiar de modelo: uno suprime una vacilación literal en el pasaje de las 39 enmiendas; el otro traduce parcialmente al gallego una frase de la transcripción en castellano. Ambos quedaron fuera por la misma regla de coincidencia literal que se aplicó a GLM.

**Diarización heredada.** L012 y L013 usan las etiquetas originales de S0027–S0028, donde ya habíamos observado un cambio de turno mal reflejado por ElevenLabs. No puede deducirse a partir de `speaker_2` que esas frases pertenecen al grupo del turno anterior. El ensayo no resolvió identidades personales.

## Los controles negativos y los asuntos

En cinco controles no aparece la inferencia prohibida, generalmente porque el pasaje se omite. N02 se registra como **incidencia relacionada**: no inventa un año a partir de «noventa e catro, noventa e cinco» ni reemplaza «desa gama» por una entidad concreta, pero introduce el destinatario no respaldado de L015. No se reescribe la prohibición del control para contarlo como un fallo exacto, ni se presenta como un control limpio.

El catálogo de Luna contiene 12 asuntos y 13 menciones. Reutiliza el presupuesto general al volver a aparecer, mantiene separado el voto particular y agrupa las actuaciones del crédito extraordinario bajo ese crédito, sin inventar el año ni una identidad precisa para la piscina. Aun así, aparecen rótulos amplios como fiscalidad, política social y política de vivienda, y un único asunto de ejecución para 2024–2025. Más asuntos no significa mejores identidades. Esa granularidad requiere un contrato más concreto y casos propios de evaluación.

## Tiempo, tokens y suscripción

| Medida del pase de extracción y asuntos | GLM | Luna mediante Codex |
|---|---:|---:|
| Operaciones de modelo | 7 | 6 |
| Ampliaciones de contexto | 1 | 0 |
| Tiempo de ejecución | 280 s | 152,6 s |
| Tokens de entrada informados | 25.491 | 33.681 |
| Tokens de salida informados | 18.438 | 7.271 |
| Registros guardados | 56 | 28 |
| Rechazados por validación | 8 | 2 |
| Duplicados textuales guardados | 33 | 0 |

El cliente informa además de 550 tokens de razonamiento para Luna. Se conservan los contadores originales sin sumarlos otra vez al total de salida; no se usa esta tabla como una facturación homogénea entre proveedores. Las entradas de Luna incluyen el contexto de Codex y un catálogo de asuntos distinto. La prueba breve de conexión consumió otros 2.481 tokens de entrada y 25 de salida, separados del pase. El trabajo posterior de revisión del asistente no está incluido.

**Luna utilizó los límites de la suscripción de ChatGPT.** No se contrató acceso por API, no se cambió de modelo durante el pase y no se amplió la cuota de ElevenLabs. La [documentación oficial de autenticación](https://learn.chatgpt.com/docs/auth) distingue el acceso por suscripción del uso facturado por clave de API; el [modo no interactivo](https://learn.chatgpt.com/docs/non-interactive-mode) reutiliza la autenticación guardada.

La [API comercial de Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) publica 0,20 USD por millón de tokens de entrada, 0,02 con caché y 1,20 de salida. La equivalencia orientativa de los contadores guardados sería alrededor de 0,0155 USD bajo esos supuestos. **No es un cargo de este ensayo ni una medición de una petición a esa API.** Para una integración futura mediríamos el transporte real y su consumo; no extrapolaríamos capacidad o costes de producción desde la suscripción.

## Comprobaciones y siguiente decisión

Se comprobaron las huellas de la referencia y del código original, la igualdad de las tres entradas iniciales y la ausencia de herramientas externas. Las seis respuestas de Luna se pueden recuperar con la inferencia bloqueada. Importarlas dos veces mantiene 12 asuntos, 13 menciones, 28 afirmaciones, 28 apariciones y 29 citas, sin duplicaciones. Las respuestas y el manifiesto originales de GLM permanecen intactos. Los resultados están en [las comprobaciones del pase](luna-checks.json).

Este ensayo sí justifica seguir probando Luna: logra una mejora observable sin reescribir el flujo. Ahora priorizaría **cobertura y abstención ante ambigüedades**, junto con citas copiadas por el programa y campos temporales separados. Antes de atribuirle una ventaja general o integrar nada, repetiríamos la versión mejorada sobre esta referencia y después sobre otro pleno no usado para ajustar las instrucciones.

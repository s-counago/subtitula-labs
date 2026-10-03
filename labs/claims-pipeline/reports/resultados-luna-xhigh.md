# Luna low frente a xhigh · Vigo 23/12/2025

Ensayo completado con GPT-5.6 Luna mediante la suscripción de ChatGPT y el cliente oficial Codex. Se reutilizaron la transcripción, los bloques, el esquema y las instrucciones del pase low. La referencia de 25 casos y seis controles permaneció congelada y fuera de las peticiones al modelo.

El resultado estricto pasa de **9/25 a 12/25** casos fieles. El pase xhigh usa **3,36 veces** los tokens totales y tarda **11,31 veces** lo observado en low. Son resultados de una ejecución completada por esfuerzo, sin medición de la variación entre repeticiones.

[Explorar xhigh con citas y audio](explorador-luna-xhigh.html) · [Explorar low](explorador-luna.html) · [Contadores conservados](luna-effort-metrics.json) · [Protocolo](../docs/comparacion-luna-xhigh.md)

## Calidad, tiempo y consumo

| Medida | Luna low | Luna xhigh |
|---|---:|---:|
| Casos fieles / 25 | 9 | 12 |
| Casos parciales | 5 | 7 |
| Casos incorrectos dirigidos a la referencia | 0 | 0 |
| Casos omitidos | 11 | 6 |
| Registros guardados | 28 | 89 |
| Candidatos rechazados por el programa | 2 | 11 |
| Duplicados exactos | 0 | 0 |
| Operaciones del modelo | 6 | 6 |
| Tokens de entrada | 33.681 | 43.285 |
| Entrada leída de caché | 0 | 0 |
| Tokens de salida, incluido razonamiento | 7.271 | 94.428 |
| De la salida: tokens de razonamiento | 550 | 73.766 |
| Total: entrada + salida | 40.952 | 137.713 |
| Tiempo del pase completado | 2 min 32,6 s | 28 min 45,6 s |
| Equivalencia orientativa a precios API | 0,015461 USD | 0,121971 USD |

**El razonamiento ya está incluido en la salida; no se suma otra vez al total.** Los tokens de entrada incluyen instrucciones, esquema y contexto repetido en cada operación. La referencia es una selección previa, no una anotación exhaustiva: estos resultados no miden precisión global ni certifican todos los registros guardados.

## Intentos y límites del recuento

El primer intento xhigh se interrumpió al alcanzar el límite local de 360 segundos en el primer bloque. No dejó respuesta final ni contador de uso. Tras inspeccionar el registro, se repitió con 900 segundos de margen por operación; los datos y parámetros de inferencia se mantuvieron. La tabla corresponde a ese segundo pase completado.

**El consumo total de todos los intentos xhigh es desconocido**, porque falta el contador del intento interrumpido. No se le asigna un consumo de cero. También se excluyen del pase las comprobaciones mínimas de transporte: low, 2.481 de entrada y 25 de salida; xhigh, 2.483 de entrada y 60 de salida (33 de razonamiento incluidos). La comprobación xhigh duró 4,718 segundos y coincidió con la espera del primer bloque del pase completado. El trabajo del evaluador queda fuera de estos contadores.

## Qué casos cambian

| Caso | Afirmación de referencia | Low | Xhigh |
|---|---|---|---|
| G01 | O 23 de decembro de 2025 celébrase o décimo noveno orzamento consecutivo deste goberno municipal. | Omitido | Parcial [X002](explorador-luna-xhigh.html#X002) |
| G02 | O orzamento incrementa en 700.000 euros a bolsa de alugueiro. | Fiel | Fiel [X008](explorador-luna-xhigh.html#X008) |
| G03 | A política social nos orzamentos municipais incrementouse un 696,5 % entre 2007 e 2026. | Fiel | Omitido  |
| G04 | As bolsas de inglés para cursar estudos no estranxeiro pasan a ter 3.325.000 euros. | Fiel | Fiel [X010](explorador-luna-xhigh.html#X010) |
| G05 | O orzamento incrementa nun 7 % os recursos para cultura. | Omitido | Fiel [X022](explorador-luna-xhigh.html#X022) |
| G06 | O copagamento a Sogama subiu de 86 a 104,50 euros por tonelada en 2025. | Omitido | Fiel [X083](explorador-luna-xhigh.html#X083) |
| G07 | O proxecto de orzamentos levado ao pleno é o mesmo aprobado inicialmente, salvo un par de correccións de erros materiais. | Parcial | Parcial [X029](explorador-luna-xhigh.html#X029) [X031](explorador-luna-xhigh.html#X031) |
| G08 | Foron rexeitadas as 198 emendas do BNG ao proxecto de orzamentos municipais. | Omitido | Fiel [X032](explorador-luna-xhigh.html#X032) |
| G09 | As axudas sociais municipais foron recortadas nun 50 % nos últimos cinco anos. | Fiel | Omitido  |
| G10 | Propúxose elevar o Plan Municipal de Emprego ata 3 millóns de euros. | Parcial | Omitido  |
| G11 | Propúxose mobilizar case 10 millóns de euros adicionais para o acceso á vivenda. | Omitido | Omitido  |
| G12 | O BNG comprométese a defender mediante un voto particular que se estimen as alegacións da Asociación Veciñal de Teis. | Omitido | Parcial [X033](explorador-luna-xhigh.html#X033) |
| G13 | A taxa do lixo increméntase ata un 50 % segundo os casos. | Parcial | Parcial [X043](explorador-luna-xhigh.html#X043) |
| G14 | En 2024 quedaron sen executar 100 millóns de euros. | Fiel | Fiel [X044](explorador-luna-xhigh.html#X044) |
| G15 | No terceiro trimestre de 2025, a execución global situábase por debaixo do 40 %. | Fiel | Fiel [X045](explorador-luna-xhigh.html#X045) |
| G16 | As emendas que o grupo municipal presentou ao orzamento sumaban un importe global de 72,3 millóns de euros. | Parcial | Parcial [X050](explorador-luna-xhigh.html#X050) |
| G17 | Propúxose elevar ata 26 millóns de euros os recursos para vivenda. | Fiel | Fiel [X051](explorador-luna-xhigh.html#X051) |
| G18 | O grupo do falante anuncia que votará en contra das contas presentadas. | Omitido | Parcial [X063](explorador-luna-xhigh.html#X063) |
| G19 | Na bancada do Partido Popular había só catro concelleiros ese día. | Omitido | Omitido  |
| G20 | O falante afirma que o orzamento municipal ten os impostos máis baixos de Galicia. | Omitido | Fiel [X070](explorador-luna-xhigh.html#X070) |
| G21 | A política social contempla exencións de impostos por un volume de ata 16 millóns para quen non pode pagar. | Fiel | Fiel [X067](explorador-luna-xhigh.html#X067) |
| G22 | O falante anuncia que o orzamento será aprobado ese día con 19 votos de 27 concelleiros, o 70 %. | Omitido | Omitido  |
| G23 | O orzamento preséntase como un orzamento sen débeda. | Omitido | Fiel [X069](explorador-luna-xhigh.html#X069) |
| G24 | O voto particular foi rexeitado por 7 votos a favor, 19 en contra e ningunha abstención. | Parcial | Parcial [X088](explorador-luna-xhigh.html#X088) |
| G25 | Os Orzamentos Xerais do Concello para 2026 quedaron aprobados por 19 votos a favor, 7 en contra e ningunha abstención. | Fiel | Fiel [X089](explorador-luna-xhigh.html#X089) |

La [evaluación anotada](evaluation-luna-xhigh.json) explica cada decisión de xhigh y distingue lo que el modelo nunca generó de lo que el programa rechazó. Se mantiene la misma rúbrica: sujeto, valor, periodo, condiciones, modalidad y evidencia.

## Errores observados

- **XE01** [X002](explorador-luna-xhigh.html#X002) [X029](explorador-luna-xhigh.html#X029) [X030](explorador-luna-xhigh.html#X030) [X031](explorador-luna-xhigh.html#X031) [X033](explorador-luna-xhigh.html#X033) [X063](explorador-luna-xhigh.html#X063) [X088](explorador-luna-xhigh.html#X088): El tratamiento temporal sigue fallando: algunos actos reciben el año del presupuesto y el ordinal del presupuesto queda sin periodo pese a tener fecha explícita en la cita. La fecha de aparición y el periodo de la afirmación necesitan distinguirse.
- **XE02** [X043](explorador-luna-xhigh.html#X043): La subida máxima del lixo mantiene porcentaje y condición, pero omite el periodo de referencia, como en low.
- **XE03** [X050](explorador-luna-xhigh.html#X050): Une cantidad de enmiendas e importe global en una sola propiedad y valor; conserva la cifra autocorregida, pero no la atomicidad.
- **XE04** : Ocho candidatos del primer bloque se rechazan: siete incluyen una clave de asunto no declarada y dos una cita no literal respecto de sus segmentos; un candidato acumula ambos motivos. G03, G09 y G10 se pierden aquí. El bloque alcanza los máximos de 15 asuntos y 40 afirmaciones, sin que ello demuestre por sí solo la causa de las referencias inválidas.
- **XE05** [X040](explorador-luna-xhigh.html#X040) [X041](explorador-luna-xhigh.html#X041) [X042](explorador-luna-xhigh.html#X042): Limitación heredada de la transcripción: S0027–S0028 siguen etiquetados como speaker_2 pese al anuncio de turno del Grupo Popular. No debe usarse esa etiqueta para atribuir el contenido al grupo anterior.
- **XE06** [X076](explorador-luna-xhigh.html#X076) [X080](explorador-luna-xhigh.html#X080): Marca como reported_statement afirmaciones propias del orador sobre deuda de la Xunta y uso de fondos para Sogama. Las citas no presentan esas frases como palabras de otra persona; añadir según el orador no basta para esa modalidad estructurada.
- **XE07** [X087](explorador-luna-xhigh.html#X087): La propiedad expresa sentido de la votación, pero valueText contiene setenta e dous millóns en lugar de en contra. El texto conserva ambos datos, mientras que la pareja estructurada propiedad–valor resulta incoherente.
- **XE08** : El segundo bloque genera dos afirmaciones de S0041, que solo era contexto vecino; el programa las rechaza por pertenecer a otro bloque. El tercer bloque sí las genera en su ámbito correcto, evitando duplicarlas en los registros guardados.

Motivos de rechazo — pueden coincidir varios en un candidato: claim_belongs_to_context_not_current_block: 2; quote_not_literal: 3; unknown_matter_key: 7.

## Controles negativos

- **N01**: No guarda la cita de Besteiro como una observación directa sobre este pleno. Los candidatos 33–35 del primer bloque atribuían correctamente el discurso referido, pero se rechazaron por una clave de asunto no declarada. La ausencia guardada no se presenta como un acierto de cobertura.
- **N02**: Omite el pasaje de 1,3 millones, desa gama y noventa e catro, noventa e cinco. No normaliza la secuencia ambigua ni reproduce el destinatario sin apoyo observado en L015 de low; la omisión no acredita capacidad general de resolver esa ambigüedad.
- **N03**: No identifica ni corrige silenciosamente Concello da Torre. No extrae ese pasaje.
- **N04**: No completa la frase cortada del año siguiente ni inventa un compromiso concreto a partir de ella.
- **N05**: No identifica a la persona ni convierte creo que en certeza sobre su cargo. X074 y X075 extraen otras afirmaciones sobre impuestos y crédito en Ferrol; no resuelven la identidad incierta del control.
- **N06**: Extrae el paro cercano al 4 %, conserva una cita literal continua y anota la secuencia ASR pago, paro como incertidumbre. No crea un indicador de pago ni añade una definición estadística del porcentaje.

## Precio de Luna

La [ficha oficial de GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) publica estas tarifas estándar, comprobadas el 11 de septiembre de 2026:

| Tipo | USD por millón de tokens |
|---|---:|
| Entrada | 0,20 |
| Entrada leída de caché | 0,02 |
| Salida | 1,20 |

El esfuerzo de razonamiento no cambia la tarifa por token. Puede aumentar el consumo. Los [tokens de razonamiento se facturan como salida](https://developers.openai.com/api/docs/guides/reasoning). Estos ensayos utilizaron los límites de la suscripción: las equivalencias anteriores **no son cargos de API ni facturas**. No incluyen la transcripción, realizada una sola vez antes de los ensayos. Los contadores proceden de Codex y no de una petición comercial medida por API.

No hubo lecturas ni escrituras de caché informadas. Las escrituras de caché tienen un multiplicador de 1,25 sobre la entrada normal; las peticiones de más de 272.000 tokens de entrada aplican multiplicadores adicionales. Los bloques utilizados están por debajo de ese umbral. Véase la [ficha de tarifas guardada](../docs/luna-pricing-2026-09-11.json).

## Alcance

Se evalúa fidelidad a la transcripción automática de una sesión pública, sin comprobar veracidad externa ni cotejar el audio caso por caso. La anomalía de diarización S0026–S0028 sigue presente en la fuente. La agrupación de asuntos no tiene una métrica exhaustiva de identidad en esta versión. La comparación no demuestra que xhigh siempre mejore ni justifica integrar automáticamente estas salidas en la aplicación.

Las [comprobaciones sin nuevas inferencias](luna-xhigh-checks.json) verifican las entradas iniciales, las huellas de referencia y versiones, la reutilización de respuestas y la importación idempotente.

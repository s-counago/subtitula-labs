# Sol medium frente a Luna low y xhigh · Vigo 23/12/2025

Ensayo solicitado el 12 de septiembre de 2026: misma transcripción, tres bloques iniciales, instrucciones, esquemas, validadores y resolución de asuntos. Se cambió el modelo y el esfuerzo sin aplicar las mejoras propuestas. La referencia permaneció congelada y fuera de las peticiones.

Sol recupera **16/25 casos completos (64 %)**, con 6 parciales y 3 omitidos. La misma medida dio 9/25 en Luna low y 12/25 en Luna xhigh. **Es recuperación de una selección previa, no precisión global de las salidas.**

[Explorar Sol con citas y audio](explorador-sol.html) · [Evaluación anotada](evaluation-sol.json) · [Contadores](sol-comparison-metrics.json) · [Protocolo](../docs/comparacion-sol.md)

## Comparación

| Medida | Luna low | Luna xhigh | Sol medium |
|---|---:|---:|---:|
| Casos fieles / 25 | 9 | 12 | 16 |
| Casos parciales | 5 | 7 | 6 |
| Casos incorrectos dirigidos a la referencia | 0 | 0 | 0 |
| Casos omitidos | 11 | 6 | 3 |
| Registros guardados | 28 | 89 | 69 |
| Candidatos rechazados | 2 | 11 | 0 |
| Duplicados exactos | 0 | 0 | 0 |
| Operaciones del modelo | 6 | 6 | 7 |
| Tokens de entrada | 33.681 | 43.285 | 62.547 |
| Entrada leída de caché | 0 | 0 | 2.432 |
| Tokens de salida, incluido razonamiento | 7.271 | 94.428 | 30.989 |
| De la salida: razonamiento | 550 | 73.766 | 11.270 |
| Total: entrada + salida | 40.952 | 137.713 | 93.536 |
| Tiempo del pase completado | 2 min 32,6 s | 28 min 45,6 s | 10 min 49,4 s |
| Equivalencia orientativa a precios API | 0,015461 USD | 0,121971 USD | 0,861213 USD |

**El razonamiento ya está incluido en la salida; no se suma dos veces.** Los contadores incluyen instrucciones, esquema y contexto repetido. Se usaron los límites de la suscripción de ChatGPT; la equivalencia API no es un cargo ni una factura.

Sol realizó 1 ronda de contexto adicional, prevista por v1, sobre la frase ambigua «desa gama» del segundo bloque. La segunda extracción sustituye a la primera para validar y guardar; ambas operaciones y todos sus tokens se contabilizan. Los pases Luna no pidieron esa ronda. Las extracciones finales por bloque generaron 69 candidatos, de los que se guardaron 69. No hubo reintentos ni prueba de conexión separada en Sol.

La tabla usa los pases completados. El primer intento xhigh terminó al alcanzar 360 segundos sin contador de uso; su consumo es desconocido y queda fuera. También se excluyen las pequeñas pruebas de transporte de Luna, conservadas en las métricas. Sol y xhigh completado tuvieron el mismo límite de espera de 900 segundos por operación; low tuvo 360. El trabajo del evaluador y la transcripción original no están incluidos.

## Los 25 casos

| Caso | Afirmación esperada | Luna low | Luna xhigh | Sol medium |
|---|---|---|---|---|
| G01 | O 23 de decembro de 2025 celébrase o décimo noveno orzamento consecutivo deste goberno municipal. | Omitido | Parcial | Omitido  |
| G02 | O orzamento incrementa en 700.000 euros a bolsa de alugueiro. | Fiel | Fiel | Fiel [S004](explorador-sol.html#S004) |
| G03 | A política social nos orzamentos municipais incrementouse un 696,5 % entre 2007 e 2026. | Fiel | Omitido | Fiel [S006](explorador-sol.html#S006) |
| G04 | As bolsas de inglés para cursar estudos no estranxeiro pasan a ter 3.325.000 euros. | Fiel | Fiel | Fiel [S007](explorador-sol.html#S007) |
| G05 | O orzamento incrementa nun 7 % os recursos para cultura. | Omitido | Fiel | Fiel [S012](explorador-sol.html#S012) |
| G06 | O copagamento a Sogama subiu de 86 a 104,50 euros por tonelada en 2025. | Omitido | Fiel | Fiel [S063](explorador-sol.html#S063) |
| G07 | O proxecto de orzamentos levado ao pleno é o mesmo aprobado inicialmente, salvo un par de correccións de erros materiais. | Parcial | Parcial | Fiel [S015](explorador-sol.html#S015) |
| G08 | Foron rexeitadas as 198 emendas do BNG ao proxecto de orzamentos municipais. | Omitido | Fiel | Fiel [S016](explorador-sol.html#S016) |
| G09 | As axudas sociais municipais foron recortadas nun 50 % nos últimos cinco anos. | Fiel | Omitido | Fiel [S018](explorador-sol.html#S018) |
| G10 | Propúxose elevar o Plan Municipal de Emprego ata 3 millóns de euros. | Parcial | Omitido | Parcial [S020](explorador-sol.html#S020) |
| G11 | Propúxose mobilizar case 10 millóns de euros adicionais para o acceso á vivenda. | Omitido | Omitido | Parcial [S022](explorador-sol.html#S022) |
| G12 | O BNG comprométese a defender mediante un voto particular que se estimen as alegacións da Asociación Veciñal de Teis. | Omitido | Parcial | Parcial [S028](explorador-sol.html#S028) |
| G13 | A taxa do lixo increméntase ata un 50 % segundo os casos. | Parcial | Parcial | Fiel [S032](explorador-sol.html#S032) |
| G14 | En 2024 quedaron sen executar 100 millóns de euros. | Fiel | Fiel | Fiel [S034](explorador-sol.html#S034) |
| G15 | No terceiro trimestre de 2025, a execución global situábase por debaixo do 40 %. | Fiel | Fiel | Fiel [S035](explorador-sol.html#S035) |
| G16 | As emendas que o grupo municipal presentou ao orzamento sumaban un importe global de 72,3 millóns de euros. | Parcial | Parcial | Fiel [S039](explorador-sol.html#S039) |
| G17 | Propúxose elevar ata 26 millóns de euros os recursos para vivenda. | Fiel | Fiel | Fiel [S040](explorador-sol.html#S040) |
| G18 | O grupo do falante anuncia que votará en contra das contas presentadas. | Omitido | Parcial | Parcial [S051](explorador-sol.html#S051) |
| G19 | Na bancada do Partido Popular había só catro concelleiros ese día. | Omitido | Omitido | Omitido  |
| G20 | O falante afirma que o orzamento municipal ten os impostos máis baixos de Galicia. | Omitido | Fiel | Fiel [S055](explorador-sol.html#S055) |
| G21 | A política social contempla exencións de impostos por un volume de ata 16 millóns para quen non pode pagar. | Fiel | Fiel | Parcial [S053](explorador-sol.html#S053) |
| G22 | O falante anuncia que o orzamento será aprobado ese día con 19 votos de 27 concelleiros, o 70 %. | Omitido | Omitido | Omitido  |
| G23 | O orzamento preséntase como un orzamento sen débeda. | Omitido | Fiel | Fiel [S054](explorador-sol.html#S054) |
| G24 | O voto particular foi rexeitado por 7 votos a favor, 19 en contra e ningunha abstención. | Parcial | Parcial | Parcial [S068](explorador-sol.html#S068) |
| G25 | Os Orzamentos Xerais do Concello para 2026 quedaron aprobados por 19 votos a favor, 7 en contra e ningunha abstención. | Fiel | Fiel | Fiel [S069](explorador-sol.html#S069) |

Se mantienen los criterios de periodo, condiciones, modalidad, atomicidad y evidencia. Una aparición de otra voz o segmento no sustituye al caso esperado. La evaluación anotada explica las pérdidas durante generación o validación.

## Errores observados en Sol

- **SE01** [S020](explorador-sol.html#S020) [S022](explorador-sol.html#S022): Omite en las propuestas normalizadas la condición de rechazo atribuida al gobierno; esa información sobrevive solo en las citas. Son G10 y G11.
- **SE02** [S028](explorador-sol.html#S028) [S051](explorador-sol.html#S051) [S068](explorador-sol.html#S068): Persiste la confusión entre año presupuestario y fecha del acto: los dos compromisos llevan 2026 y la votación del voto particular recibe la fecha incorrecta 2026-12-23.
- **SE03** [S053](explorador-sol.html#S053): Clasifica como propuesta la afirmación sobre las exenciones fiscales contenidas en la política presupuestaria, aunque conserva sus condiciones y cifra en el texto.
- **SE04** [S029](explorador-sol.html#S029) [S030](explorador-sol.html#S030) [S031](explorador-sol.html#S031): Limitación de la fuente: conserva speaker_2 en S0027–S0028, pese al anuncio anterior del turno del Grupo Popular. Esa etiqueta no permite atribuir estas afirmaciones al grupo de la intervención anterior.
- **SE05** : No recupera tres casos positivos: el ordinal de los 19 presupuestos, los cuatro concejales presentes y el anuncio de aprobación con 19/27 votos y el 70 %. Se pierden en generación, sin intervención de los validadores.
- **SE06** [S002](explorador-sol.html#S002): Amplía el sujeto de la frase presupuestaria con deuda cero al Concello de Vigo en general y le asigna la fecha de la sesión. La cita no concreta el perímetro contable; esta normalización es más amplia que el presupuesto descrito en el segmento.

Motivos de rechazo, con posible solapamiento: ninguno.

## Controles negativos

- **N01**: No extrae la cita de Besteiro ni la presenta como una observación directa sobre este pleno municipal.
- **N02**: Solicita contexto para desa gama en S0029. Tras recibirlo, anota que sigue sin un referente identificable y omite el importe de 1,3 millones. No normaliza noventa e catro, noventa e cinco ni asigna una entidad concreta.
- **N03**: No extrae el pasaje de Concello da Torre ni corrige silenciosamente su entidad.
- **N04**: No completa la frase truncada del año siguiente ni fabrica un compromiso concreto a partir de ella.
- **N05**: No resuelve la identidad o cargo de la persona mencionada con creo que. S056 y S057 usan S0054 como contexto geográfico para otras afirmaciones de S0055 sobre Ferrol, sin eliminar la incertidumbre de identidad del control.
- **N06**: Extrae el paro cercano al 4 %, conserva la cita literal con dun pago, dun paro y señala la autocorrección como incertidumbre. No crea un indicador de pago ni añade una definición estadística.

## Precios y límites de la comparación

Tarifas oficiales consultadas el 11–12 de septiembre de 2026: [Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna), [Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol).

| USD por millón de tokens | Luna | Sol |
|---|---:|---:|
| Entrada | 0,20 | 4,00 |
| Entrada leída de caché | 0,02 | 0,40 |
| Salida | 1,20 | 20,00 |

Las escrituras de caché tienen un multiplicador de 1,25 sobre la entrada normal. Sol informó de 2.432 tokens de entrada leídos de caché y ninguna escritura; ambos pases Luna informaron de cero lecturas y escrituras. Todas las operaciones están por debajo de 272.000 tokens de entrada. Los equivalentes utilizan contadores de Codex, no peticiones comerciales medidas por API.

La revisión mide fidelidad a la transcripción de una única sesión. No verifica la verdad de las afirmaciones ni coteja el audio caso por caso. La referencia fue seleccionada inicialmente por Sol y revisada por el asistente principal antes de los ensayos; no constituye una evaluación humana independiente. La agrupación de asuntos tampoco tiene una métrica exhaustiva en v1. Una ejecución por configuración no permite medir variación ni generalizar estos porcentajes.

[Comprobaciones sin inferencias nuevas](sol-checks.json): entradas iniciales iguales a GLM y ambos pases Luna, huellas conservadas, respuestas reutilizables, contadores verificados y doble importación sin duplicados.

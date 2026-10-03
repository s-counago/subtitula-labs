# Sol medium sobre el mismo proceso

El 12 de septiembre de 2026 el usuario pidió comparar Sol medium sin aplicar ninguna de las mejoras propuestas. Este ensayo mantiene el proceso v1: la misma transcripción completa, los mismos tres bloques iniciales de hasta 9.000 caracteres, dos segmentos vecinos, instrucciones, esquemas, límites de elementos, recuperación de contexto, validadores, resolución de asuntos y persistencia.

Solo cambian el modelo a `gpt-5.6-sol` y el esfuerzo a `medium`. La configuración toma el mismo margen de espera de 900 segundos del pase xhigh completado. Las tarifas y el nombre de ejecución cambian únicamente en los registros del experimento. No se incorpora ninguna corrección de citas, periodos, atomicidad, cobertura o dependencia entre afirmaciones y asuntos.

## Reproducción

La ejecución es `vigo-2025-12-23-sol-medium-v1`, mediante `scripts/sol_pipeline.py` y `config/sol-experiment.json`. El adaptador hereda la inferencia del cliente Codex y la resolución del programa original sin cambiarlas. Conserva las huellas del programa original, el adaptador, la nueva configuración y la referencia. La única adaptación de la persistencia es el cálculo de equivalencia API con tarifas de Sol, porque el adaptador anterior contenía las tarifas de Luna.

Antes de la primera llamada se comprobaron las tres entradas iniciales contra low y xhigh y se guardaron las huellas de 26 archivos de las ejecuciones previas y de la referencia. Los prompts no contienen la referencia. Los catálogos que reciban las etapas posteriores pueden diferir porque dependen de lo que haya producido el modelo.

Se usó la misma sesión de suscripción y el cliente oficial Codex, sin herramientas ni acceso al laboratorio desde el proceso del modelo. El máximo era nueve operaciones, incluidos posibles pedidos de contexto. Se completaron siete: tres extracciones iniciales, una extracción con contexto adicional y tres resoluciones de asuntos. No hubo interrupciones, reintentos ni una prueba de conexión separada.

## Comparación y contabilidad

Se mantuvo la rúbrica de 25 casos y seis controles. El resultado estricto mide recuperación completa de esos casos, no precisión global de todas las salidas. Sol obtuvo 16 fieles, 6 parciales y 3 omitidos; los tres se perdieron en generación. No hubo rechazos técnicos. Los errores permanecen en los resultados originales. Una ejecución por configuración no mide variabilidad entre repeticiones.

Los tokens de razonamiento ya están incluidos en la salida. El total es entrada más salida; incluye instrucciones y contexto repetido. La equivalencia API no es facturación de estos pases por suscripción. La [ficha oficial de Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol), consultada el 12 de septiembre, indica 4 USD/M de entrada, 0,40 de entrada en caché y 20 de salida. Las escrituras de caché tienen un multiplicador de 1,25 sobre la entrada normal. Estos bloques están por debajo del umbral de 272.000 tokens de entrada por petición que activa otras tarifas.

Las comparaciones de tiempo y consumo utilizan los pases completados. El primer intento xhigh interrumpido, de consumo desconocido, y las pequeñas pruebas de transporte de Luna siguen excluidos e identificados por separado.

## Resultado conservado

El pase tardó 649,365 segundos y guardó 69 afirmaciones de 69 candidatos finales por bloque, sin duplicados exactos; 32 asuntos, 35 menciones y 73 citas. La ronda de contexto de S0029 no resolvió «desa gama» y el modelo omitió ese importe ambiguo. La nueva extracción sustituyó la primera del segundo bloque, conforme al programa original; el consumo de ambas está incluido.

Codex informó de 62.547 tokens de entrada, de los cuales 2.432 eran lecturas de caché, y 30.989 de salida, incluidos 11.270 de razonamiento. Total: 93.536. Equivalencia API: 0,8612128 USD, sin ser un cargo de estos ensayos por suscripción.

[Informe comparativo](../reports/resultados-sol.md), [evaluación](../reports/evaluation-sol.json), [métricas](../reports/sol-comparison-metrics.json) y [explorador](../reports/explorador-sol.html). Las [comprobaciones](../reports/sol-checks.json) verificaron las tres entradas iniciales contra GLM y ambos pases Luna, 26 archivos previos sin modificaciones, todas las huellas, las siete respuestas reutilizadas sin inferencia, los contadores contra sus eventos y dos importaciones idénticas.

Para regenerar solo comprobaciones e informes, sin llamadas al modelo:

```text
python scripts/verify_sol.py
python scripts/render_sol_comparison.py
python scripts/render_report.py --config config/sol-experiment.json --suffix=-sol --label "Sol medium" --id-prefix S
```

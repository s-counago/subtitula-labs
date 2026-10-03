# Criterios de revisión del ensayo

Se anotan correspondencias entre los 25 casos congelados y las propuestas guardadas. El programa solo preselecciona coincidencias por segmentos y etiqueta de voz; el asistente revisa su significado. Compartir segmento no se considera un acierto automático.

Cada caso obtiene uno de cuatro estados:

- **Fiel:** recupera la afirmación principal, mantiene sujeto, valor, condiciones, periodo y carácter de hecho, propuesta o compromiso. La evidencia sostiene esa lectura.
- **Parcial:** recupera el núcleo, pero omite o altera un matiz importante, une afirmaciones que deberían separarse o utiliza mal la modalidad estructurada.
- **Omitido:** no hay una propuesta guardada que recupere esa afirmación. Se diferencia si el modelo nunca la generó o si se rechazó durante la validación.
- **Incorrecto:** hay una propuesta claramente dirigida al caso pero cambia el sujeto, importe, dirección de la afirmación u otro elemento central.

El resultado estricto considera solo «fiel». Se informa también de la recuperación del núcleo cuando sea útil, sin presentar los parciales como aciertos completos. La fidelidad del texto y la modalidad estructurada se explican por separado cuando difieren.

Los seis controles negativos se revisan buscando concretamente la inferencia que deben evitar. No son seis afirmaciones que el modelo esté obligado a producir. Un resultado vacío para un control puede ser adecuado, pero no demuestra capacidad de detectar todas las ambigüedades.

La revisión del resto de salidas recoge errores observados y ejemplos útiles. No se usa la ausencia de un caso en la referencia como señal de falso positivo: la referencia no es exhaustiva. La agrupación de asuntos se revisa por sus decisiones y fuentes; no hay una métrica exhaustiva de identidad o granularidad en v1.

Se registran asimismo fallos técnicos, rechazos de citas, solicitudes de contexto, llamadas, tiempos y tokens. Los tokens totales de peticiones incluyen instrucciones, esquema y contexto repetido: no equivalen al tamaño de la transcripción tokenizada una vez.

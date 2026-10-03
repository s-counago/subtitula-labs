# Preparación de fixtures y medición de eficiencia

22/09/2026. **No se ha llamado a Jev en esta preparación.** Las 24 peticiones están congeladas; las respuestas empleadas en los tests son fabricadas y temporales. La precisión, estabilidad y latencia del modelo siguen sin medir.

El [catálogo](../fixtures/v2/README.md) contiene cuatro extracciones reales, siete controles del primer ensayo y trece variantes nuevas. Cubre las cinco etiquetas posibles. Solo tres de las cuatro extracciones reales se puntúan: R03 queda exploratoria por una equivalencia de programa aún dudosa. No hay 24 hechos reales independientes ni una referencia humana validada.

[Verificación local](fixtures-v2-verification.json): 16 tests pasan, incluidas las diez simulaciones de fallo técnico; huellas y enlaces locales comprobados. No existen archivos de respuestas reales del proveedor.

## Qué sabemos antes de tener la clave

| Pase | Llamadas previstas | Bytes JSON enviados | Preguntas | Escenario de tokens de entrada | Equivalente orientativo USD |
|---|---:|---:|---:|---:|---:|
| Smoke diagnóstico | 6 | 25.672 | 13 | 6.813–16.121 | 0,000286–0,000677 |
| Completo diagnóstico | 24 | 112.392 | 59 | 29.890–71.108 | 0,001255–0,002987 |
| Completo con filtro previo | 21 | 98.310 | 52 | 26.159–62.302 | 0,001099–0,002617 |

Los bytes, preguntas y llamadas salen de las peticiones preparadas. **Los tokens y dólares son escenarios ilustrativos, no intervalos garantizados ni consumo observado.** Se calculan como caracteres JSON / 4 + 32 por pregunta, y caracteres JSON / 2 + 256 por pregunta. No usamos el tokenizador del proveedor y su serialización interna puede diferir.

La equivalencia usa la tarifa directa publicada de **0,042 USD por millón de tokens de entrada**, sin cargo por salida, consultada el 22/09/2026 en [TypeSafe Models](https://docs.typesafe.ai/models). No presupone saldo disponible, importe mínimo de compra ni facturación final. Excluye búsqueda, extracción de PDF, preparación/revisión, impuestos y cualquier coste de pasarela. Los planes verificables están en [full-plan.json](fixtures-v2-full-plan.json) y [smoke-plan.json](fixtures-v2-smoke-plan.json).

El filtro previo ahorra **3 de 24 llamadas (12,5 %)** en esta selección: C03 no tiene evidencia; C04 y F07 solo reproducen declaraciones. Es un ahorro de llamadas comprobable sin inferencia. No demuestra una mejora de precisión; la correcta clasificación previa del tipo de fuente sigue siendo necesaria. El modo diagnóstico conserva esas llamadas para comprobar si Jev sabe abstenerse.

## Qué mediremos al ejecutar

- **Calidad:** coincidencia con referencia, falsos apoyos y falsas refutaciones por separado, número de predicciones de cada tipo y matriz de confusión. Separar casos reales y controles; no mezclar sus porcentajes.
- **Utilidad tras controles:** propuestas retenidas, errores entre ellas y cobertura sobre casos completados puntuables. Una tasa de error baja con cobertura casi nula puede ser poco útil. Un fallo HTTP no entra en el denominador de precisión, pero permanece visible como fallo técnico.
- **Estabilidad:** cambios de etiqueta entre paráfrasis, idiomas, distractores, orden de fuentes y contenido malicioso; cambios entre llamadas repetidas. Una etiqueta estable también puede ser incorrecta.
- **Tiempo:** p50 y p95 de llamadas HTTP exitosas. Son descripciones de una muestra pequeña, no un SLA. No incluyen recuperación documental ni tiempo humano; esos tiempos requieren instrumentar después el flujo completo.
- **Coste:** tokens declarados por el proveedor y su equivalencia a tarifa directa. Un timeout o error sin uso declarado queda con consumo desconocido, nunca como llamada gratuita. Con consumo completo, dividir el coste del pase entre propuestas retenidas correctas da una medida auxiliar de coste por propuesta útil; si no hay ninguna, esa medida no se calcula.

La confianza mínima de 0,85 es una regla provisional para experimentar. No está calibrada y no transforma la probabilidad de salida en probabilidad de verdad. Las relaciones por pasaje las calcula el mismo Jev: que coincidan con la valoración global no es una validación independiente.

## Orden recomendado

1. Con la clave local, ejecutar el pase `smoke` para comprobar acceso y contrato. Preservar cualquier error antes de corregirlo.
2. Ejecutar `full` en otro `run-id` y revisar el informe completo, especialmente las refutaciones y apoyos que la referencia no permite. Smoke + full suman hasta 30 llamadas por tener cachés separadas.
3. Usar `replay` para inspeccionar métricas y decisiones sin más consumo. Si cambia el evaluador, conservar el informe previo junto a la versión del código para que la comparación sea rastreable.
4. Ejecutar las nueve llamadas de `repeatability` si interesa observar estabilidad. Nunca repetir selectivamente hasta conseguir una etiqueta deseada.
5. Antes de una integración, ampliar y revisar la referencia con otros plenos, fuentes contradictorias reales y datos reservados por familia de afirmación. Seguir los hitos del [plan de mitigación](../docs/mitigacion-fallos-jev.md).

La preparación no añade un buscador automático de fuentes, no inicia la aplicación y no habilita publicación. Los pasajes existentes permiten ensayar la clasificación; la eficiencia del proceso completo depende también de cuánto cueste recuperar evidencia suficiente.

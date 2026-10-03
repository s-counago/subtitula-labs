# Laboratorio de afirmaciones y asuntos

Ensayo independiente de Subtitula, iniciado el 11 de septiembre de 2026. Trabaja con una grabación municipal pública y archivos locales. No conecta con la base de datos de la aplicación ni publica perfiles o afirmaciones.

**Decisión del usuario, 12 de septiembre:** se elige Luna xhigh por el equilibrio de coste y calidad observado. La nueva [exploración de búsqueda y experiencia del portal](ideas/de-afirmaciones-a-respuestas-2026-09-12.md) propone usar las afirmaciones como memoria derivada junto a fragmentos de transcripción, con fuentes visibles en la respuesta. Es una propuesta de producto, no una integración ni una nueva ejecución de modelos.

El objetivo es entender y probar el recorrido **transcripción → apariciones de afirmaciones → asuntos → comparación con una referencia revisada**. Usamos ElevenLabs para transcribir; el primer pase empleó GLM-4.7-Flash en Workers AI y los siguientes GPT-5.6 Luna, con razonamiento low y xhigh, y GPT-5.6 Sol medium mediante la suscripción de ChatGPT en Codex. El cotejo documental sigue pendiente.

**Comparación con Sol medium completada, sin cambiar el proceso:** [informe](reports/resultados-sol.md), [explorador](reports/explorador-sol.html), [métricas](reports/sol-comparison-metrics.json) y [protocolo](docs/comparacion-sol.md). Sol recupera 16/25 casos fieles (64 %), con 6 parciales y 3 omitidos; Luna low obtuvo 9 y xhigh 12 fieles. Guarda 69 afirmaciones sin rechazos técnicos ni duplicados exactos. Consume 93.536 tokens y tarda 10:49, incluida una ronda opcional de contexto. Equivalencia API: 0,8612128 USD; se usaron límites de suscripción. Esta medida es recuperación de la referencia, no precisión global.

**Comparación low–xhigh completada:** [informe y tokens](reports/resultados-luna-xhigh.md), [explorador de xhigh](reports/explorador-luna-xhigh.html) y [protocolo](docs/comparacion-luna-xhigh.md). Xhigh pasa de 9 a 12 casos fieles de 25, con 7 parciales y 6 omitidos. Usa 137.713 tokens frente a 40.952 y tarda 28:46 frente a 2:33. El primer intento xhigh llegó al límite de espera y carece de contador de uso; no está incluido en esos totales. La comparación conserva los errores, la referencia y todos los intentos.

**Comparación con Luna completada:** [informe comparativo](reports/resultados-luna.md), [explorador de Luna](reports/explorador-luna.html) y [protocolo](docs/comparacion-luna.md). Con la misma referencia y el mismo recorrido: nueve casos fieles, cinco parciales y 11 omitidos; 28 registros guardados sin duplicados exactos. Mejora frente a GLM, pero persisten omisiones e interpretaciones sin apoyo. No se repitió la transcripción.

**Primer ensayo completado:** [resultados y errores](reports/resultados.md), [explorador con citas y audio](reports/explorador.html) y [diagrama y pseudocódigo](docs/pipeline.md). Se transcribió una sesión completa de Vigo, se congelaron 25 casos antes de GLM y se ejecutó v1. La extracción todavía no es fiable: cinco casos parcialmente recuperados, dos incorrectos y 18 omitidos. Los resultados se conservan para comparaciones futuras.

| Directorio | Contenido |
|---|---|
| `inputs/sources/` | Procedencia, selección y metadatos de la sesión |
| `inputs/media/` | Audio utilizado y datos técnicos |
| `inputs/transcripts/` | Respuesta original del transcriptor y segmentos legibles |
| `reference/` | Casos revisados y huella de congelación anterior a GLM |
| `config/` | Parámetros y esquemas, sin credenciales |
| `scripts/` | Operaciones reproducibles y validaciones |
| `runs/` | Peticiones, respuestas, decisiones y registros de cada ejecución |
| `reports/` | Comparación, errores, consumo y conclusiones |
| `ideas/` | Mejoras todavía no incorporadas |

Las claves se leen de archivos locales privados o variables del entorno y nunca se guardan en los resultados. Las ejecuciones consumen las cuotas existentes autorizadas por el usuario; no contratan servicios ni modifican despliegues.

La referencia no representa la verdad del mundo: indica qué afirmaciones esperamos extraer fielmente de ciertos pasajes. El resto de la sesión también se procesa, pero no se considera exhaustivamente anotado.

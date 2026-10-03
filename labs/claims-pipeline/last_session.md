# Estado del laboratorio · 12 de septiembre de 2026

**Última decisión y exploración:** el usuario elige Luna xhigh por coste y pide conectar el almacenamiento de afirmaciones con la búsqueda ciudadana. [Propuesta](ideas/de-afirmaciones-a-respuestas-2026-09-12.md): fuentes versionadas, memoria derivada e índices/proyecciones; recuperar tanto fragmentos como afirmaciones, componer según la intención y mostrar fuentes. Los parciales pueden ayudar a localizar, pero no se asumen fiables para fechas/cálculos. La maqueta de conversación usa tres respuestas preparadas con citas reales del laboratorio; no hay búsqueda ni generación en directo. Se propone comparar fragmentos, afirmaciones y ambos con preguntas de usuarios. No se ejecutó el nuevo ensayo, se modificó la extracción ni se integró o desplegó nada.

**Último trabajo: Sol medium comparado sin aplicar las mejoras propuestas.** Petición expresa del usuario: mismo proceso. [Informe](reports/resultados-sol.md), [explorador](reports/explorador-sol.html), [métricas](reports/sol-comparison-metrics.json) y [protocolo](docs/comparacion-sol.md).

- `vigo-2025-12-23-sol-medium-v1`, `gpt-5.6-sol`, esfuerzo medium. Hereda inferencia y resolución sin cambios. Conserva transcripción, prompts, contratos, validación y referencia. Límite de espera de 900 segundos por operación, igual al xhigh completado. No modificar su adaptador/configuración, congelados por huella.
- Siete operaciones en 649,365 segundos, incluida una ronda prevista de contexto para «desa gama». La ambigüedad quedó sin resolver y se omitió ese importe. Sin reintentos ni prueba de conexión separada.
- 69 candidatos finales por bloque, todos guardados; cero rechazos y duplicados exactos, 32 asuntos, 35 menciones, 73 citas. La primera extracción del segundo bloque fue sustituida por la de contexto, conforme a v1; sus tokens también cuentan.
- Referencia: 16 fieles, 6 parciales, 0 incorrectos dirigidos a los casos y 3 omitidos, frente a 9/5/0/11 en Luna low y 12/7/0/6 en xhigh. Es recuperación, no precisión global de las 69 salidas. Persisten pérdidas de condiciones, errores de periodo y modalidad; G24 recibe 2026-12-23 en lugar de 2025-12-23.
- Uso: 62.547 entrada (2.432 de caché) + 30.989 salida = 93.536 tokens; 11.270 de razonamiento ya incluidos en salida. Equivalencia API 0,8612128 USD a tarifas 4/0,40/20 USD por millón. Se usaron límites de la suscripción, no facturación medida de API.
- [Verificación](reports/sol-checks.json): tres entradas iniciales iguales a GLM y ambos Luna; 26 archivos previos y todas las huellas intactos; siete respuestas reutilizadas sin inferencia, contadores contrastados con eventos y doble importación idempotente. Explorador comprobado con búsqueda y salto desde la referencia.
- No se aplicó ninguna mejora a la extracción ni se repitió transcripción, integró en la app, desplegó o hizo commit. Se conserva la evidencia previa y no se inició otro ensayo.

**Trabajo anterior: comparación Luna low–xhigh completada.** El usuario pidió el pase extra high, sus tokens frente a low y el precio. [Informe](reports/resultados-luna-xhigh.md), [explorador xhigh](reports/explorador-luna-xhigh.html), [métricas](reports/luna-effort-metrics.json) y [protocolo](docs/comparacion-luna-xhigh.md).

- El primer intento, `vigo-2025-12-23-luna-xhigh-v1`, alcanzó 360 segundos sin respuesta ni contador. Se conserva como interrumpido; su consumo es desconocido. Después de inspeccionar los registros, `vigo-2025-12-23-luna-xhigh-v1b` completó con un límite de 900 segundos por operación. No hubo reintentos automáticos.
- Mismas entradas, instrucciones, esquema, validadores y recorrido que low; esfuerzo xhigh. Seis operaciones, 100 candidatos, 89 guardados, 11 rechazados, cero duplicados exactos, 25 asuntos y 41 menciones. Sin contexto adicional ni herramientas del modelo.
- Misma referencia: 12 fieles, 7 parciales, 0 incorrectos dirigidos a los casos y 6 omitidos; low: 9/5/0/11. La revisión no mide precisión global. Se documentan errores temporales, de atomicidad, modalidad y propiedad–valor; tres casos se pierden en validación.
- Xhigh completado: 43.285 entrada + 94.428 salida = 137.713 tokens; 73.766 de razonamiento incluidos en salida. Low: 33.681 + 7.271 = 40.952; 550 de razonamiento incluidos. Duraciones: 1.725,615 frente a 152,631 segundos. Equivalencia API: 0,1219706 frente a 0,0154614 USD, sin representar cargos de esta ejecución por suscripción.
- Se excluyen del pase la comprobación mínima de transporte xhigh (2.483 entrada, 60 salida, 33 de razonamiento incluidos), la de low y el intento interrumpido sin uso. El total de todos los intentos xhigh no puede calcularse.
- Comprobada igualdad de las tres entradas iniciales, todas las huellas, seis respuestas reutilizadas sin inferencia y doble importación sin duplicados: [verificación](reports/luna-xhigh-checks.json). Para repetir solo comprobaciones: `python scripts/verify_luna.py --config config/luna-xhigh-long-experiment.json --suffix=-luna-xhigh --id-prefix X`.
- Precio oficial consultado el 11 de septiembre: 0,20 USD/M entrada, 0,02 entrada en caché y 1,20 salida; [ficha](docs/luna-pricing-2026-09-11.json). El esfuerzo no cambia la tarifa por token. No se modificó la aplicación ni se repitió la transcripción.

Siguiente trabajo propuesto: simplificar el contrato de extracción, copiar las citas desde el programa y separar fecha del acto de año presupuestario antes de asumir que más razonamiento basta. No se ejecutó una nueva versión ni otro corpus.

**Trabajo anterior: comparación con Luna low completada.** El usuario pidió repetir el pase mediante la suscripción. Se usó el cliente oficial Codex 0.153.4 con la sesión ChatGPT existente y `gpt-5.6-luna`, razonamiento low. El adaptador `scripts/luna_pipeline.py` ejecuta el mismo recorrido de v1 sin cambiar instrucciones, esquema ni validadores. Se conservan las diferencias del transporte en [el protocolo](docs/comparacion-luna.md).

- Nueva ejecución: `runs/vigo-2025-12-23-luna-v1`. Seis operaciones y una prueba previa de conexión separada; sin consultas de contexto ni llamadas a herramientas.
- 28 registros guardados de 30 candidatos, dos rechazos de cita, cero duplicados exactos; 12 asuntos y 13 menciones.
- Referencia: nueve fieles, cinco parciales, cero incorrectos dirigidos a los casos y 11 omitidos. N02 tiene un error relacionado de interpretación financiera fuera de los positivos; no presentar el resultado como libre de errores.
- 152,6 segundos; 33.681 tokens de entrada y 7.271 de salida informados por Codex, incluidos 550 de razonamiento. Usa los límites de la suscripción; la equivalencia API no es facturación.
- [Informe comparativo](reports/resultados-luna.md), [explorador](reports/explorador-luna.html), [evaluación](reports/evaluation-luna.json) y [comprobaciones](reports/luna-checks.json).
- Comprobadas la igualdad de las tres entradas iniciales con GLM, las huellas originales y la importación idempotente; las seis respuestas se reutilizan sin inferencia. No modificar el adaptador ni su configuración para reanudar esta ejecución: están versionados por huella.
- Para comprobar otra vez sin inferencia: `python scripts/verify_luna.py`. Para generar el explorador: `python scripts/render_report.py --config config/luna-experiment.json --suffix=-luna --label Luna --id-prefix L`.

Siguiente iteración propuesta: cobertura, abstención ante referencias ambiguas, copia de citas desde el programa y separación de fecha del acto/año presupuestario. No se ejecutó v2 ni otra transcripción.

El usuario pidió pasar la exploración a pseudocódigo, trabajar fuera de la aplicación y ejecutar un ensayo real con ElevenLabs y GLM, revisando 20–30 casos antes de la inferencia. Completado en este directorio independiente.

- Corpus: pleno extraordinario de Vigo, 23/12/2025, grabación completa de 26:55.
- ElevenLabs Scribe v2: 4.356 palabras, 67 segmentos, cinco etiquetas de voz; 1.795 créditos informados. La clave actual bastó. No se creó una clave dedicada ni se modificaron cuotas.
- Referencia: 25 casos y seis controles, seleccionados por Sol y revisados por el asistente principal. Congelada antes de GLM; no modificarla para mejorar cifras.
- GLM v1: siete llamadas; 25.491 tokens de entrada y 18.438 de salida; 0,00890466 USD de generación estimada a tarifa de catálogo.
- Resultado: 56 registros candidatos guardados, ocho rechazados, 33 duplicados textuales entre los guardados. Comparación: cero casos plenamente fieles, cinco parciales, dos incorrectos y 18 omitidos. Ver [informe](reports/resultados.md).
- Comprobada la reutilización de siete respuestas sin red y la importación idempotente local. No se compararon inferencias nuevas entre sí.
- Limitaciones conocidas: diarización S0026–S0028, modalidad mal aplicada, inversión de actor, listas repetidas, errores de citas y escasa cobertura.

Siguiente trabajo propuesto: simplificar el extractor y separar la resolución de asuntos, conservando v1. Una mejora sobre esta referencia sería desarrollo con conjunto conocido; luego hará falta un corpus independiente. No iniciar cotejo documental, otros proveedores o integración sin una nueva decisión de alcance.

Todas las credenciales siguen en sus ubicaciones privadas originales. Los scripts leen claves sin mostrarlas; la sesión local de Cloudflare se renovó con Wrangler. No se ha cambiado código de Subtitula, infraestructura ni despliegues. No se ha hecho commit.

Explorador comprobado visualmente con búsqueda, filtros y salto temporal del audio; ver [comprobación de navegador](reports/browser-checks.json). Al entregar el ensayo queda un servidor temporal en `http://127.0.0.1:8767/reports/explorador.html`, limitado a este equipo, con el audio pausado. Si deja de estar disponible, se puede reiniciar con `python scripts/serve.py` desde el laboratorio; los archivos del informe permanecen disponibles sin servidor.

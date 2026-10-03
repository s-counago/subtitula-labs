# Pase de Luna xhigh sobre el mismo flujo

El usuario pidió otro intento con Luna en xhigh, una comparación de tokens con low y el precio del modelo. Se conserva la misma referencia, transcripción, segmentación, esquema, instrucciones y cliente oficial que en el pase low. El único parámetro de inferencia que cambia es `model_reasoning_effort`, de low a xhigh.

**Completado:** el segundo intento terminó el 11 de septiembre, a las 23:59 de Madrid; la revisión y entrega se cerraron el 12. [Informe con resultados](../reports/resultados-luna-xhigh.md): 12 casos fieles, 7 parciales y 6 omitidos, frente a 9/5/11 en low. Xhigh guardó 89 de 100 candidatos, sin duplicados exactos; 25 asuntos y 41 menciones. Seis operaciones, ninguna ronda extra de contexto, 28 minutos y 45,6 segundos.

Los contadores del pase completado son 43.285 tokens de entrada y 94.428 de salida: 137.713 en total. De la salida, 73.766 son razonamiento. Frente a low son 3,36 veces los tokens totales y 11,31 veces el tiempo. La equivalencia a tarifa API pasa de 0,0154614 a 0,1219706 USD, 7,89 veces. No es una factura ni incluye el intento interrumpido de uso desconocido.

## Registro de intentos

- `runs/vigo-2025-12-23-luna-xhigh-v1`: el primer bloque alcanzó el límite local de 360 segundos. El proceso no dejó respuesta final ni contador de uso. Se conserva como interrumpido, sin asignarle cero tokens ni una puntuación de calidad.
- `runs/vigo-2025-12-23-luna-xhigh-v1b`: nuevo intento con un margen local de 900 segundos por operación, después de inspeccionar los eventos y registrar la decisión de recuperación. El tiempo de espera cambia; el prompt, los datos y los parámetros de inferencia se mantienen.
- `runs/luna-xhigh-transport-probe`: comprobación mínima sin corpus, realizada durante la espera del segundo intento. Respondió en 4,718 segundos, con 2.483 tokens de entrada, 60 de salida y 33 de razonamiento incluidos en la salida. Se cuenta aparte de la pipeline.

La respuesta de esa comprobación acredita que esta configuración puede responder a una petición mínima. No explica por sí sola la duración del análisis del bloque ni mide su calidad.

El cliente informa del uso al completar el turno. Si se interrumpe antes, este laboratorio no obtiene un contador parcial fiable. Por eso el consumo agregado de todos los intentos xhigh seguirá siendo desconocido mientras uno de ellos carezca de recibo, aunque otro termine. Una equivalencia API del pase completado no debe presentarse como el coste total de todos los intentos.

## Qué se comparó

Se aplicó la misma rúbrica de 25 casos y seis controles. No se añadieron al prompt ejemplos que faltaban en low. Las respuestas posteriores pueden producir distintas consultas de contexto y diferentes catálogos; esa variación es resultado de ejecutar el mismo programa con otro esfuerzo. En este pase no se solicitó contexto adicional. Las tres entradas iniciales, los esquemas y las instrucciones coinciden exactamente con low y GLM.

Los contadores se leen de los recibos del cliente. El total de tokens es entrada más salida; el razonamiento es un subconjunto de la salida. Los tokens distintos del razonamiento no equivalen necesariamente a contar el texto visible, porque el formato también puede intervenir. El trabajo del evaluador y las pruebas mínimas se mantienen fuera de los totales de la pipeline.

Una ejecución completada por esfuerzo permite describir resultados observados; no estima la variabilidad entre repeticiones ni prueba que aumentar el esfuerzo siempre mejore la extracción. La ejecución usa los límites de la suscripción, como el pase low. Las [comprobaciones](../reports/luna-xhigh-checks.json) acreditan la preservación de las entradas y referencia, la reutilización sin inferencia de las seis respuestas y la importación idempotente.

## Precio de la API

La [ficha oficial de Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) publica 0,20 USD por millón de tokens de entrada, 0,02 con caché y 1,20 de salida. El esfuerzo no tiene una tarifa por token distinta; el coste puede aumentar si genera más tokens. El razonamiento se factura como salida, según [la guía oficial](https://developers.openai.com/api/docs/guides/reasoning).

Las escrituras de caché tienen un multiplicador de 1,25 sobre la entrada sin caché. Las peticiones de más de 272.000 tokens de entrada tienen multiplicadores adicionales; estos bloques están muy por debajo de ese umbral. Se conserva una [ficha de tarifas](luna-pricing-2026-09-11.json). Son precios de API comercial, no cargos de los ensayos realizados con la suscripción.

# Comparación de v1 con Luna mediante la suscripción

El usuario pidió repetir el pase de GLM con Luna usando la suscripción de ChatGPT. Se utiliza `gpt-5.6-luna` mediante el modo no interactivo del cliente oficial Codex, que ya tiene una sesión de ChatGPT iniciada. El programa no extrae credenciales ni convierte la suscripción en una clave de la API comercial.

## Qué se mantiene

- La grabación y la transcripción originales, sin volver a transcribir.
- Los 67 segmentos, sus etiquetas de voz y los mismos tres bloques de 9.000 caracteres como máximo, con dos segmentos vecinos.
- Las instrucciones originales de extracción y resolución de asuntos, sin añadir ejemplos de los fallos de GLM.
- Los esquemas JSON, los límites de elementos, las comprobaciones de citas y voces, y el guardado en SQLite.
- Una ampliación de contexto como máximo por bloque, mediante la misma función de recuperación local.
- La referencia congelada de 25 casos y seis controles, con la misma rúbrica de evaluación. No se incluye en las entradas de Luna.

El adaptador importa y ejecuta el recorrido original. Sustituye el transporte de inferencia y la contabilidad de uso; no reescribe los pasos de extracción, validación o resolución. Las respuestas y los datos de Luna se guardan en `runs/vigo-2025-12-23-luna-v1`, junto a una referencia al ensayo de GLM. Las consultas posteriores dependen de lo que genere cada modelo: mantener el mismo programa no exige obligar a Luna a pedir el contexto que pidió GLM.

## Diferencias que afectan a la comparación

Esto compara **GLM mediante Workers AI** con **Luna mediante Codex**, no dos peticiones idénticas a una misma API. Las instrucciones de tarea de v1 sustituyen las instrucciones incorporadas de Codex mediante `model_instructions_file`. Aun así, Codex añade contexto de ejecución y su gestión de salida.

Se configura Luna con razonamiento `low`. GLM se ejecutó con thinking desactivado. Codex no expone aquí los mismos controles de temperatura, semilla y máximo de tokens de salida; por eso no se presentan como parámetros igualados. Sí se conservan los máximos de afirmaciones, asuntos y contexto del contrato.

Cada operación inicia una sesión efímera desde un directorio temporal vacío. Se excluyen las instrucciones del proyecto y el catálogo de habilidades, se deshabilitan la búsqueda web y las herramientas de shell, aplicaciones, navegador y delegación. La ejecución registra los eventos del cliente y excluye una respuesta si observa actividad inesperada de herramientas. Esto evita que el extractor consulte por su cuenta los resultados o la referencia. Las advertencias de arranque del cliente se conservan como advertencias, no como llamadas a herramientas.

La prueba inicial de conexión utiliza listas vacías y no contiene material del pleno. Su consumo queda separado del ensayo. Una advertencia de arranque hizo que el adaptador clasificase inicialmente esa respuesta como actividad de herramientas; se comprobó el archivo ya guardado y se corrigió esa clasificación sin hacer una segunda inferencia.

## Consumo

Las operaciones usan los límites de la suscripción. Los contadores de tokens del cliente se conservan por operación; no se interpretan como una factura ni como una medición exacta del porcentaje de suscripción consumido. El trabajo de revisión del asistente también consume suscripción y está fuera de esos contadores del extractor.

La API comercial de Luna tiene precios propios. Cualquier equivalencia calculada con sus tarifas y contadores de Codex sería orientativa: incluye contexto del cliente y depende de la semántica de esos contadores. No es el importe cobrado en este ensayo ni garantiza el coste de una futura integración por API.

## Referencias oficiales consultadas el 11 de septiembre de 2026

- [Autenticación de Codex](https://learn.chatgpt.com/docs/auth): acceso con ChatGPT y acceso mediante clave de API tienen contratos de uso distintos.
- [Modo no interactivo](https://learn.chatgpt.com/docs/non-interactive-mode): autenticación guardada, eventos JSON y salida conforme a esquema.
- [Configuración de Codex](https://learn.chatgpt.com/docs/config-file/config-reference): instrucciones, habilidades, herramientas y opciones de razonamiento.
- [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna): modelo y tarifas de la API comercial.

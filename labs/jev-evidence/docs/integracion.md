# Integración propuesta

Jev encaja después de recuperar fuentes. El extractor existente conserva qué se dijo; Jev propone qué relación tiene esa afirmación con unos pasajes concretos. Un cambio en esa relación no modifica la declaración original.

## Contrato comprobado

La [API oficial](https://docs.typesafe.ai/api) recibe `model`, `state` y un mapa `questions`; cada pregunta `choice` contiene `instructions` y `criteria`. Devuelve `choice`, probabilidades por opción, confianza, versión del modelo y uso. Las preguntas se evalúan independientemente: una pregunta no puede depender de la respuesta de otra en la misma llamada.

La [documentación de modelos](https://docs.typesafe.ai/models), consultada el 22/09/2026, identifica `jev-1.13.0`, entrada textual y tarifa directa de 0,042 USD por millón de tokens de entrada, sin cargo por salida. El inglés es su idioma de entrenamiento principal. Las instrucciones de este ensayo están en inglés y las pruebas mantienen las afirmaciones y fuentes originales en gallego/castellano; no se ha medido equivalencia entre idiomas.

La [página de limitaciones](https://docs.typesafe.ai/model-jaggedness/jev-1.13) reconoce dificultades con aritmética, fechas, razonamiento indirecto, contexto irrelevante y contenido adversarial. Por eso conviene resolver cálculos y comparaciones de fechas en código, usar pasajes breves y comprobar abstención. Un JSON válido no garantiza una conclusión correcta.

## Flujo propuesto para una futura integración

1. Seleccionar una aparición de afirmación cuya extracción sea fiel, manteniendo hablante, revisión de transcripción, cita y tiempo. Dividir proposiciones compuestas cuando se puedan separar sin cambiar su sentido.
2. Buscar fuentes para la entidad, propiedad, periodo y fase concretos. Buscar posibles apoyos y refutaciones. Estudios sirven para proposiciones generales; presupuestos, contratos, registros o liquidaciones suelen ser más adecuados para hechos municipales.
3. Registrar URL, emisor, fecha del documento y de consulta, pasaje, página, huella, versión, disponibilidad histórica y dependencia respecto de otras fuentes. Una nota reproducida por cinco medios constituye una misma cadena de procedencia.
4. Normalizar cifras, unidades, impuestos y fechas con operaciones comprobables. En el caso de Sogama el runner calcula `95 × 1,10 = 104,50`, condicionado a la aplicación del canon reducido. No deduce que Vigo haya cumplido los requisitos ni que haya pagado una factura concreta.
5. Enviar a Jev la afirmación, contexto necesario y pasajes. Pedir relación global y relación por pasaje con IDs cerrados. Para tareas complejas, separar decisiones y combinarlas después en código.
6. Validar esquema, IDs, probabilidades y versión. Persistir propuesta, corpus exacto, parámetros, respuesta, consumo y versión de la política. Si falta evidencia, conservar `insufficient` y el motivo para recuperar más documentación.
7. Medir contra casos revisados y reservados antes de adoptar umbrales. El porcentaje de confianza se usa como señal interna, no como porcentaje de verdad ni valoración de una persona.

En la arquitectura actual, el trabajo asíncrono correspondería al procesador existente y la persistencia canónica a Spring/PostgreSQL. Los documentos y respuestas grandes podrían guardarse en R2. Un adaptador serviría tanto a la API directa como al [modelo `typesafe/jev` de Cloudflare](https://developers.cloudflare.com/ai/models/typesafe/jev/). Esta descripción es un diseño, no código integrado o desplegado.

Un registro futuro de evaluación podría enlazar `claimOccurrenceId`, `transcriptRevision`, `evidenceBundleHash`, `sourceVersionIds`, `modelVersion`, `questionVersion`, `assessment`, `sourceRelations`, `providerDistribution`, `createdAt` y `reviewState`. Recalcular ante correcciones y conservar las versiones anteriores. No guardar un único booleano `isTrue` sobre la afirmación.

## Búsqueda, coste y siguientes pruebas

El coste completo incluye localizar, leer, convertir y seleccionar evidencia, además de Jev. Es probable que esas tareas dominen el tiempo en un corpus municipal; este ensayo no mide un sistema automático de recuperación. Se pueden reutilizar documentos por asunto y evaluar varias afirmaciones sobre el mismo paquete cuando sea pequeño, cuidando que cada pregunta tenga alcance independiente.

Antes de integrar: añadir transcripciones distintas, fuentes que discrepen de forma real, documentos de otro año, versiones corregidas, homónimos, tablas con impuestos y casos no verificables. Reservar un conjunto de prueba que no se use para ajustar preguntas. Medir falsas refutaciones, falso apoyo, abstención, recuperación de fuentes y tiempo humano. Once casos seleccionados por el asistente solo prueban el recorrido y algunos errores concretos.

La publicación de verificaciones queda sujeta al diseño editorial y las fases canónicas existentes. Este laboratorio no juzga honestidad, intención, ideología ni carácter de hablantes.

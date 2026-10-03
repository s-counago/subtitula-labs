# De las afirmaciones a una experiencia de transparencia

Estado: propuesta exploratoria del 12 de septiembre de 2026, apoyada en el experimento de Vigo. No implementa búsqueda nueva, respuestas generativas ni publicación. El usuario elige **Luna xhigh** por el equilibrio observado entre calidad y coste; no se vuelven a ejecutar los modelos ni se modifican los resultados congelados.

## Qué papel tienen las afirmaciones

Las afirmaciones son una memoria estructurada y derivada de lo dicho. Facilitan recuperar cifras, propuestas y declaraciones, agrupar apariciones y, cuando exista evidencia suficiente, comparar periodos. No son por sí mismas el contenido principal del portal ni sustituyen a las fuentes.

Guardar la transcripción completa no obliga a enviarla completa a un modelo por consulta. Un índice encuentra fragmentos, y el sistema recupera su texto y contexto solo cuando resultan pertinentes. Por tanto, la justificación de extraer afirmaciones debe ser la mejora en las tareas del usuario, no solo la reducción del tamaño del texto.

La base propuesta conserva tres representaciones conectadas:

| Representación | Contenido | Función |
|---|---|---|
| Fuente versionada | Grabación, revisión de transcripción, segmentos, tiempos y voces; documentos cuando se incorporen | Evidencia y cobertura de lo no extraído |
| Memoria derivada | Afirmaciones y apariciones, asuntos concretos, temas, intervenciones y decisiones sustentadas | Estructurar, relacionar y comparar sin perder atribución |
| Proyecciones de consulta | Índices de palabras y significado, fichas/resúmenes con fuentes y cachés vinculadas a versiones | Encontrar y presentar resultados con rapidez |

No implica tres bases de datos. La arquitectura existente puede mantener metadatos y relaciones en PostgreSQL, medios en R2 e índices léxicos y pgvector. Estos últimos son reconstruibles. El experimento no demuestra que una base de grafos o un catálogo perfecto de asuntos sea necesario.

El nombre de una persona solo se conserva como identidad cuando está confirmado. En este corpus las etiquetas de voz no equivalen a nombres. La fecha del pleno procede de la sesión; no se reemplaza por el periodo escrito por el extractor. Una afirmación puede referirse a 2026 y haberse formulado en diciembre de 2025.

## Cómo llega una consulta a una respuesta

1. Interpretar lo solicitado: tema, ayuntamiento u organismo explícito, intervalo temporal y tipo de tarea. «Qué se propuso», «quién habló», «cuándo» y «qué se ejecutó» necesitan respuestas diferentes. Mantener la consulta original y no inventar filtros.
2. Buscar sobre fragmentos de transcripción **y** representaciones derivadas mediante palabras y significado. La entrada del ciudadano es única; no necesita escoger entre búsqueda léxica y semántica.
3. Reunir y ordenar candidatos. Una afirmación puede llevar a un pasaje; un pasaje sin afirmación también debe entrar. Agrupar repeticiones sin contar una guía, una afirmación y su segmento como tres fuentes independientes.
4. Recuperar evidencia y contexto de la revisión publicada: quién habla, asunto, sesión, negaciones, condiciones y fragmentos vecinos cuando hagan falta. Comprobar de nuevo publicación activa antes de componer y servir.
5. Elegir presentación. Para una consulta de tema, intervenciones agrupadas; para una cifra, respuesta breve atribuida; para «quién», voces/personas confirmadas agrupadas; para «cuándo», cronología. Las preguntas de evolución o recuentos completos exigen recorrer las ocurrencias relevantes con paginación, no resumir solo los primeros resultados.
6. Cuando la recuperación esté evaluada, componer un resumen breve con fuentes por afirmación, acompañado de los pasajes que lo sustentan. Si falta evidencia, devolver los resultados útiles y explicar el límite. Tener citas no demuestra por sí solo que la redacción esté sustentada; también se evalúan condiciones, atribución y alcance.

Una pregunta sobre vivienda puede atravesar varios asuntos concretos: presupuesto anual, ayudas al alquiler y una obra de vivienda social. El tema amplio «vivienda» y el asunto concreto no son la misma entidad. Que una afirmación esté enlazada al presupuesto general no debe impedir recuperarla por su contenido sobre vivienda.

## El ejemplo real de este laboratorio

Consulta: **«¿Qué se dijo sobre vivienda en el presupuesto de 2026?»**

- Aumento de 700.000 euros en la bolsa de alquiler: X008 → S0006 → 01:59.
- Casi 10 millones adicionales reclamados, con rechazo atribuido al gobierno: S0019 → 08:33. Luna xhigh no guardó la afirmación correspondiente a G11. Este caso demuestra por qué la búsqueda debe tener acceso directo a los fragmentos, aunque no exista una afirmación.
- Propuesta de elevar hasta 26 millones los recursos para vivienda: X051 → S0034 → 15:05.

El usuario vería un resumen de estas posiciones con fecha y fuentes, no tres registros con campos internos. No se suman las cantidades: una es un incremento de una partida, otra una propuesta adicional y otra una dotación propuesta.

Consulta: **«¿Se llegaron a gastar los 26 millones?»**

X051 conserva una propuesta; X062 y S0035 recogen el rechazo de las enmiendas según el orador. El resultado formal de aprobar el presupuesto completo no demuestra que esa propuesta concreta se incorporase ni que se pagara. Las fuentes de esta sesión no constituyen un registro de ejecución. La respuesta debe delimitar lo que consta y reconocer que faltan fuentes posteriores de gasto. El cotejo documental continúa expresamente diferido.

## Qué aportan los parciales

Luna xhigh es la opción elegida. Una afirmación parcial puede servir para localizar un pasaje. No debería convertirse automáticamente en un dato fiable para un total, fecha, cronología o comparación. La etiqueta «parcial» pertenece a nuestra evaluación de 25 casos; no disponemos de un clasificador automático infalible que identifique todas las salidas defectuosas del corpus.

Se evita depender ciegamente de las afirmaciones: recuperar el original para la respuesta, conservar metadatos de sesión fiables y no utilizar un campo dudoso en una operación que lo necesita. Esto mantiene el objetivo de revisión humana por excepciones del plan canónico, sin imponer una aprobación manual de cada afirmación.

## Coste y prueba que falta

Trabajo al incorporar una sesión: transcribir, segmentar, extraer con Luna xhigh, indexar y preparar resúmenes recurrentes. Trabajo por consulta: recuperar candidatos, cargar un conjunto acotado de fuentes y, si se ofrece respuesta asistida, generar solo esa respuesta. Las cronologías extensas requieren una estrategia jerárquica; no se promete un presupuesto fijo para cualquier consulta. Las fichas y cachés se invalidan al corregir o retirar publicaciones, sin volver a exponer información retirada.

El siguiente experimento propuesto compara, con las mismas preguntas ciudadanas y sus fuentes esperadas: **A, solo fragmentos; B, solo afirmaciones; C, ambos**. Medir encontrar la evidencia necesaria, conservación de condiciones y atribuciones, ausencia de conclusiones sin apoyo, tiempo hasta el pasaje útil, latencia y coste por consulta. Es una propuesta de experimento, no una evaluación ya ejecutada ni una nueva autorización de gasto.

La maqueta de conversación contiene tres respuestas redactadas a partir de fuentes del laboratorio. Las interacciones solo cambian esos ejemplos y abren citas. No utiliza un buscador nuevo ni un modelo en directo, y no demuestra calidad de recuperación.

## Encaje y referencias

El [plan canónico](../../../subtitula-gal-api/docs/product/transparency-evidence-search-implementation-plan.md), secciones 7, 14 y 15, ya contempla evidencia, temas, intervenciones, índices y fuentes visibles. Las respuestas asistidas siguen condicionadas a evaluar la recuperación. La búsqueda natural por intención y agrupación de voces tiene un [diagnóstico pendiente](../../../subtitula-gal-api/docs/product/natural-language-speaker-search-2026-09-10.md). Esta exploración no gradúa esas capacidades ni modifica el plan.

- [PostgreSQL: introducción a búsqueda de texto](https://www.postgresql.org/docs/current/textsearch-intro.html): indexar y recuperar el documento seleccionado no exige reenviar todo el corpus.
- [pgvector: búsqueda híbrida](https://github.com/pgvector/pgvector#hybrid-search): combinación de similitud vectorial con búsqueda de texto y fusión/reordenación.
- [Anthropic: Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval): recuperar fragmentos y preservar contexto. Sus métricas no se trasladan a Subtitula sin un ensayo propio.

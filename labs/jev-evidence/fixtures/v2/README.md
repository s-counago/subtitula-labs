# Fixtures de cotejo v2

Preparadas el 22/09/2026, antes de llamar a Jev. Hay **24 peticiones semánticas y 10 escenarios técnicos**. Se reutilizan las cuatro extracciones del pleno de Vigo del 23/12/2025 y los siete documentos ya descargados. No se ha generado otra transcripción ni buscado un corpus adicional.

Las etiquetas de [reference.json](reference.json) son una referencia del asistente, sin revisión humana independiente. No viajan a Jev. `supported` significa respaldada por el paquete de evidencia para el alcance indicado; no significa verdad universal ni juicio sobre el hablante. Las variantes C/F son controles deliberados, no nuevas declaraciones reales.

## Catálogo

| ID | Qué comprueba | Referencia prevista |
|---|---|---|
| [R01](requests/R01.json) | Extracción real: Sogama es una sociedad pública de la Xunta | supported |
| [R02](requests/R02.json) | Extracción real: incremento presupuestado de 700.000 € para alquiler | supported |
| [R03](requests/R03.json) | Extracción real: 3.325.000 € para becas de inglés; equivalencia del programa pendiente | Exploratoria, fuera de puntuación |
| [R04](requests/R04.json) | Extracción real: subida de Sogama de 86 a 104,50 €/t; falta acreditar base y aplicación | insufficient |
| [C01](requests/C01.json) | Cambiar sociedad pública por capital 100 % de la Xunta | contradicted |
| [C02](requests/C02.json) | Multiplicar por diez el incremento para alquiler | contradicted |
| [C03](requests/C03.json) | Afirmación sin fuentes externas | insufficient |
| [C04](requests/C04.json) | Tener únicamente una noticia que reproduce un anuncio | insufficient |
| [C05](requests/C05.json) | Confundir presupuesto previsto con dinero ya pagado | insufficient |
| [C06](requests/C06.json) | Aportar un documento primario de otro asunto | insufficient |
| [C07](requests/C07.json) | Añadir instrucciones maliciosas como adjunto al contexto | supported |
| [F01](requests/F01.json) | Paráfrasis castellana de R01 | supported |
| [F02](requests/F02.json) | Paráfrasis inglesa de R01 | supported |
| [F03](requests/F03.json) | Negar la condición pública de Sogama | contradicted |
| [F04](requests/F04.json) | Afirmar algo sobre 2024 con una fuente presupuestaria de 2026 | insufficient |
| [F05](requests/F05.json) | Afirmar algo sobre Lugo con un documento de Vigo | insufficient |
| [F06](requests/F06.json) | Opinión: la política de vivienda es «excelente» | not_verifiable |
| [F07](requests/F07.json) | Triplicar una misma noticia; no son tres confirmaciones independientes | insufficient |
| [F08](requests/F08.json) | Invertir el orden de las fuentes de R04 | insufficient |
| [F09](requests/F09.json) | Rodear el pasaje pertinente de R01 con documentos de otros asuntos | supported |
| [F10](requests/F10.json) | Canon reducido condicionado: 95 € más un 10 % son 104,50 € | supported |
| [F11](requests/F11.json) | Confundir los 95 € de base con el total con IVA | contradicted |
| [F12](requests/F12.json) | Dos registros ficticios incompatibles, de la misma fase y periodo | conflicting |
| [F13](requests/F13.json) | Insertar una orden maliciosa dentro del propio pasaje documental | supported |

F12 usa dos documentos inventados del municipio ficticio «Villa Ensayo»; F13 usa una copia perturbada de un extracto. Ambos están marcados como sintéticos y carecen de URL oficial atribuida a ese contenido. F07 conserva el texto real repetido y marca una procedencia común. Las citas originales que permanecen en controles sirven para rastrear su origen; no convierten la afirmación modificada en algo que se dijo en el pleno.

R03 conserva la etiqueta original del primer ensayo, pero `scored: false`: la correspondencia entre la partida «Aulas Internacionais» y las becas de inglés no está suficientemente resuelta para imponerla como respuesta correcta. Puede cambiar esa valoración tras revisar documentación adicional, en una nueva versión de la referencia.

## Fallos técnicos sin proveedor

[transport.json](transport.json) describe escenarios fabricados para los tests; no son respuestas reales de Jev ni consumen API.

| ID | Situación | Comportamiento comprobado |
|---|---|---|
| T01 | HTTP 401 | Registrar error; detener sin reintento |
| T02 | HTTP 429 | Registrar límite; detener sin reintento |
| T03 | HTTP 529 | Registrar indisponibilidad; detener sin reintento |
| T04 | Timeout | Marcar resultado/consumo inciertos; no reenviar automáticamente |
| T05 | JSON ilegible | Preservar cuerpo recibido y rechazar |
| T06 | Falta una respuesta | Preservar cuerpo recibido y rechazar |
| T07 | Etiqueta fuera del contrato | Preservar cuerpo recibido y rechazar |
| T08 | Probabilidades inválidas | Preservar cuerpo recibido y rechazar |
| T09 | Cambia la versión del modelo | Preservar cuerpo recibido y rechazar |
| T10 | Queda un recibo de llamada interrumpida | Rechazar reenvío automático |

## Ejecutar cuando esté la clave

Desde `labs/jev-evidence`, con Python 3.11+ y `TYPESAFE_API_KEY` en el archivo local `.env` o en el entorno:

```powershell
python scripts/benchmark.py run --selection smoke --run-id fixtures-v2-smoke
```

Ese primer pase envía seis casos: R01, R02, R04, C01, C03 y C05. Si el contrato funciona, el pase completo utiliza las 24 fixtures:

```powershell
python scripts/benchmark.py run --selection full --run-id fixtures-v2-full
python scripts/benchmark.py replay --run-id fixtures-v2-full
```

Se generan `runs/<run-id>/summary.json` y `results.md`, además de peticiones, cuerpos de respuesta y recibos. `replay` recalcula el informe sin red ni claves. Repetir el mismo comando reutiliza los éxitos dentro de ese mismo pase; **smoke y full tienen cachés separadas**, de modo que ejecutar ambos implica hasta 30 llamadas. El primer fallo detiene el pase; su recibo no se borra ni se reintenta automáticamente. No abrir varios procesos sobre el mismo `run-id`.

Para probar estabilidad, un pase adicional repite tres veces R01, R04 y F13: nueve llamadas, con resultados separados por repetición.

```powershell
python scripts/benchmark.py run --selection repeatability --repeats 3 --run-id fixtures-v2-stability
```

El modo predeterminado `diagnostic` envía también los casos negativos para observar el comportamiento de Jev. El informe aplica después las reglas locales a todas las respuestas guardadas; no hace falta otro pase para analizar esas reglas. `--mode guarded` omite antes de llamar C03, C04 y F07. Si se desea medir esa ruta, usar un `run-id` distinto. Sus abstenciones locales se informan por separado y no cuentan como aciertos del modelo.

Sin clave se pueden inspeccionar costes orientativos y ejecutar todos los tests:

```powershell
python scripts/benchmark.py prepare --selection full
python -m unittest discover -s scripts -p 'test_*.py' -v
```

## Integridad y lectura de resultados

[manifest.json](manifest.json) fija las huellas de los JSON, los datos originales y el constructor de peticiones. El generador `scripts/build_fixtures.py` rechaza sobrescribir esta versión. Para cambiar preguntas, fuentes o referencia, crear otra versión; preservar los errores observados del pase anterior.

El informe separa las extracciones reales de los controles, registra falsos apoyos y falsas refutaciones, matriz de confusión, cobertura y errores después de los filtros, estabilidad de etiquetas, consumo conocido/desconocido y latencia p50/p95. R03 se muestra sin puntuar. Los tres casos reales puntuables y sus variantes están muy correlacionados: este conjunto diagnostica errores, no estima precisión general en plenos.

Leer el [informe de preparación](../../reports/fixtures-v2-preparacion.md) y el [plan de mitigación](../../docs/mitigacion-fallos-jev.md) antes de interpretar una confianza alta como autorización para publicar.

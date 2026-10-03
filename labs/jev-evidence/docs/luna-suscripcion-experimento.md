# Evaluador alternativo Luna mediante suscripción

23/09/2026. El usuario autoriza expresamente utilizar la suscripción de ChatGPT para **este experimento aislado**. La futura evaluación integrada sigue prevista con **TypeSafe por API**. No se habilita autenticación por suscripción en la aplicación ni se modifica el diseño de extracción mediante API.

## Protocolo

- Modelo solicitado: `gpt-5.6-luna`, razonamiento `xhigh`, conservando la versión del experimento de extracción previo.
- Transporte: CLI oficial Codex, sesión existente de ChatGPT; no se extraen ni copian sus credenciales. Se excluyen las variables alternativas de autenticación del proceso y se fuerza `forced_login_method="chatgpt"`.
- Cada caso usa una sesión nueva, efímera, en un directorio temporal vacío, sin configuración personal, búsqueda web, shell, aplicaciones, plugins, memoria ni agentes. Se rechaza cualquier actividad de herramientas en los eventos.
- Primer pase: los estados de las **24 fixtures v2** se conservan exactamente, junto a sus preguntas y criterios. Solo cambia el evaluador y su contrato de salida.
- Segundo pase: **cuatro afirmaciones reales**, con pasajes seleccionados automáticamente desde los siete documentos completos. No utiliza las variantes sintéticas como corpus documental.
- Referencia: las mismas etiquetas congeladas antes de inferir; R03 permanece exploratoria. Las respuestas esperadas, motivos y metadatos de puntuación no se envían al modelo.
- Máximo: 28 operaciones, una por caso y modalidad; 240 segundos por operación; sin reintentos automáticos del runner. Los reintentos internos de transporte del CLI no equivalen a réplicas planificadas y no se miden como HTTP individuales.

La [documentación oficial de autenticación](https://learn.chatgpt.com/docs/auth) describe la separación entre inicio de sesión ChatGPT y API. El [modo no interactivo](https://learn.chatgpt.com/docs/non-interactive-mode) permite conservar eventos JSON y restringir la respuesta mediante un esquema. El comportamiento concreto usado aquí se comprobó además con `codex-cli 0.154.0` instalado.

## Contrato de salida y controles

Luna devuelve `assessment`, una relación por ID de fuente, un motivo breve, los datos que faltan y citas literales. Mantiene las etiquetas `supported`, `contradicted`, `insufficient`, `conflicting` y `not_verifiable`.

**No solicitamos ni fabricamos probabilidades o confianza.** Por tanto, no aplicamos el umbral provisional 0,85 de Jev ni adaptamos la respuesta de Luna fingiendo que procede de Jev. Luna resuelve las preguntas conjuntamente; Jev las plantea de forma independiente. La comparación futura debe explicitar esa diferencia.

El diagnóstico envía todos los casos, incluidos los que permiten abstenerse localmente. Después calcula qué propuestas sobreviven a estos controles:

1. Ausencia de evidencia, evidencia compuesta solo por declaraciones reproducidas o periodos explícitos incompatibles: abstención.
2. Validación de etiquetas y del conjunto cerrado de IDs. Respuesta inválida: fallo visible, sin valoración aceptada.
3. Citas literales: comprobar que el texto citado aparece en el pasaje indicado, normalizando solo espacios. Una cita no literal se conserva como error y bloquea la propuesta; no se oculta la etiqueta original.
4. Para apoyo/refutación: exigir una relación por fuente alineada y ninguna opuesta. El resultado es una propuesta experimental, nunca publicación automática.

Los controles no prueban corrección semántica. Las relaciones por fuente provienen del mismo modelo y el filtro puede descartar conclusiones correctas que requieren combinar documentos. El periodo solo se comprueba con los metadatos disponibles o años explícitos; no es un intérprete general de fechas. No existe una comprobación determinista completa de entidad, fase o programa.

## Recuperación automática

Se extrae texto de **244 páginas PDF** —Sogama 24, memoria de Vigo 31 y gastos de Vigo 189— y de cuatro páginas HTML descargadas. El HTML excluye scripts, estilos, cabeceras, navegación, formularios y pies. No se hace OCR ni se corrigen automáticamente las tablas. El resultado son **853 fragmentos** de hasta 120 palabras, con solapamiento de 30 y procedencia por documento/página.

La consulta se construye únicamente con afirmación, territorio y periodo. BM25 usa normalización de mayúsculas/tildes y una lista pequeña de palabras vacías, sin traducción, expansión semántica ni conversión de números escritos a cifras. Selecciona seis pasajes con un máximo de dos por documento. No utiliza la etiqueta esperada, los pasajes manuales ni una lista de fuentes correctas para ordenar.

Los pasajes manuales se usan **solo después de seleccionar** para medir recuperación de documentos y cobertura de sus palabras. La cobertura léxica no acredita recuperar la cifra ni conservar el significado. Este corpus de siete documentos fue seleccionado previamente para las afirmaciones: no es una prueba de búsqueda abierta en internet.

Los cálculos condicionados originales se retiran al cambiar de paquete. Solo se reconstruyen si los fragmentos realmente recuperados contienen el canon reducido y la información del IVA requerida. Así evitamos introducir evidencia que la búsqueda no encontró.

## Archivos y ejecución

- [Entradas y manifiesto actuales](../alternatives/luna-v2/manifest.json).
- [Corpus extraído](../alternatives/luna-v2/corpus.json) y [diagnóstico de recuperación](../alternatives/luna-v2/retrieval-report.json).
- [Runner](../scripts/luna_benchmark.py), [entrada v2](../scripts/luna_subscription_v2.py), [transporte corregido](../scripts/subscription_transport_v2.py) y [recuperador](../scripts/local_retrieval.py).
- [Informe del pase](../runs/luna-subscription-v2/results.md) y [resultados estructurados](../runs/luna-subscription-v2/summary.json).

Desde `labs/jev-evidence`, la reproducción de los resultados ya guardados no hace inferencias:

```powershell
python scripts/luna_subscription_v2.py replay --run-id luna-subscription-v2
python -m unittest discover -s scripts -p 'test_*.py' -v
```

Para completar un pase interrumpido entre operaciones que terminaron correctamente:

```powershell
python scripts/luna_subscription_v2.py run --run-id luna-subscription-v2
```

Reutiliza los casos completados, verificando sus huellas. Un recibo incierto bloquea el reenvío; no borrarlo para repetir. Hay bloqueo por pase para impedir dos runners simultáneos. `--track curated` o `--track retrieved` permite escoger modalidad sin perder la caché común. `--max-new 1` limita a una operación nueva y fue utilizado para comprobar la primera respuesta sin duplicarla después.

La preparación requiere `pypdf`; se utilizó el Python incluido en el runtime de Codex. Ejecución, tests y reproducción usan la biblioteca estándar de Python y el CLI instalado. Las entradas están congeladas: cambiar documentos, preguntas o implementación requiere una nueva versión y otro pase.

## Incidencia previa y límites de interpretación

El [intento v1](../runs/luna-subscription-v1/curated-R01/receipt.json) se detuvo en la comprobación local de acceso: `--ignore-user-config` es una opción de `exec`, no del comando principal utilizado con `login status`. No se llegó a crear la invocación de inferencia ni eventos del modelo. Se conservan sus entradas, código y recibo. La v2 corrige únicamente esa comprobación; mantiene modelo, preguntas y evidencia.

Los recibos de v1 lo clasifican conservadoramente como consumo desconocido porque esa era la política genérica ante error. La inspección posterior permite precisar que fue un fallo local previo a la inferencia; no convertir ese registro en una respuesta del modelo.

El consumo se informa como tokens registrados por el CLI y uso de los límites de suscripción. No se presenta un cargo API ni se reutiliza la tarifa de Jev. La latencia incluye el transporte/contexto del CLI y no predice la latencia de TypeSafe. Los eventos de `exec` registran la configuración solicitada, pero no certifican la identidad exacta del backend resuelto.

La referencia sigue elaborada por el asistente y la muestra está muy correlacionada. Usar Luna tanto para extracción como para cotejo no constituye revisión independiente. Los resultados permiten diagnosticar esta selección; no estiman la precisión de un sistema municipal general.

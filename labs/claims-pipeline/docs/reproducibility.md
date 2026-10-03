# Ejecutar y revisar el laboratorio

Todas las rutas siguientes se resuelven desde `labs/claims-pipeline`. Python usa `requests` para las peticiones y `jsonschema` para validar. En esta máquina se ha instalado el validador exclusivamente en `.vendor/`; no es necesario modificar los entornos de Subtitula.

```powershell
python -m pip install --target .vendor -r requirements.txt
$env:PYTHONPATH = (Resolve-Path .vendor).Path
```

La transcripción se obtiene una sola vez. La clave puede venir de `ELEVENLABS_API_KEY` o de un archivo privado mediante `--env-file`. El script no muestra la clave, no la copia y no cambia su límite. Si ya existe un recibo, impide reenviar automáticamente la petición.

```powershell
python scripts/elevenlabs.py transcribe --env-file RUTA_PRIVADA --audio inputs/media/vigo-2025-12-23.mp3 --language glg
python scripts/normalize.py
```

La referencia requiere revisión real antes de congelarla. `gold-draft.json` es el borrador del revisor; `gold.json` y `frozen.json` son el conjunto aceptado y sus huellas. La comprobación de citas no sustituye revisar el significado.

```powershell
python scripts/freeze_reference.py
python scripts/check_contracts.py
python scripts/pipeline.py
```

La última operación sí puede consumir Workers AI. Usa `CLOUDFLARE_API_TOKEN` o la sesión local autenticada de Wrangler; el token no se incorpora al manifiesto ni a las peticiones guardadas. El modelo y el límite de peticiones están en `config/experiment.json`. No hay un Worker nuevo, despliegue, cola o base de datos remota.

Para volver a generar los documentos legibles y comprobar la reutilización sin red:

```powershell
python scripts/render_report.py
python scripts/review_packet.py
python scripts/verify_replay.py
```

La comparación semántica de `reports/evaluation.json` fue revisada por el asistente; esos comandos no inventan una puntuación nueva. El explorador HTML utiliza el audio local por ruta relativa. Se puede abrir en un navegador o servir este directorio en localhost; no necesita publicarse en internet.

```powershell
python scripts/serve.py
```

Abre `http://127.0.0.1:8767/reports/explorador.html`. Este servidor local admite rangos de audio para saltar directamente al minuto citado. Se detiene con Ctrl+C.

La pipeline comprueba que la referencia y la transcripción no hayan cambiado. Solo lee la huella de la referencia durante la inferencia, nunca sus casos. Cada petición guarda instrucciones, esquema, segmentos y parámetros. Cada respuesta guarda el contenido original y un recibo con duración, estado y tokens informados por el proveedor.

Una segunda ejecución con entradas idénticas reutiliza las respuestas guardadas y las claves únicas de SQLite. Una versión distinta requiere otro `experimentId`. No se reintentan automáticamente llamadas fallidas o inciertas. Los fallos de formato o evidencia se conservan para analizarlos.

## Alcance implementado de v1

- Transcripción completa con tiempos, segmentación sin reescritura lingüística y referencia previa a GLM.
- Extracción por bloques con dos segmentos vecinos y una ronda opcional de contexto de la misma sesión.
- Validación de JSON, citas, fuentes y compatibilidad de etiqueta de voz.
- Resolución de menciones contra todo el catálogo local pequeño. No usa embeddings: no necesita descartar candidatos para este tamaño.
- Persistencia transaccional local de asuntos, menciones, afirmaciones, apariciones y citas.

Cada aparición recibe inicialmente su propia afirmación. Las identidades se asignan a registros, no al texto de una frase. Agrupar automáticamente paráfrasis bajo una misma afirmación, enlazar personas entre sesiones y evaluar contradicciones siguen pendientes. Los asuntos sí pueden ser compartidos por apariciones de diferentes voces.

Una cita existente demuestra procedencia textual, no exactitud semántica ni veracidad. `reviewState=proposed` también se mantiene para las decisiones de asunto. No hay publicación automática.

## Pase comparativo con Luna

El [protocolo](comparacion-luna.md) explica el acceso por suscripción y las diferencias con una API directa. La ejecución completada se conserva en `runs/vigo-2025-12-23-luna-v1`. Para verificar sus respuestas guardadas sin inferencia y regenerar su explorador:

```powershell
python scripts/verify_luna.py
python scripts/render_report.py --config config/luna-experiment.json --suffix=-luna --label Luna --id-prefix L
```

El adaptador de inferencia es `scripts/luna_pipeline.py`; usa la autenticación de ChatGPT gestionada por el cliente oficial y no recibe claves por argumento. Una nueva versión de parámetros o código necesita otro identificador de ejecución. No se debe volver a transcribir ni modificar la referencia para una comparación sobre v1. Abrir `http://127.0.0.1:8767/reports/explorador-luna.html` con el mismo servidor local.

## Advertencia observada en la entrada

La transcripción cambia de turno después de «Turno Grupo Popular», pero conserva temporalmente la etiqueta de la intervención anterior en S0026–S0028, hasta pasar a `speaker_3` en S0029. Se conserva el ASR original para estudiar sus errores. Por tanto, una validación de consistencia con `speakerId` no acredita la identidad de quien realmente habló. Este ensayo evalúa extracción sobre esa entrada y documenta la anomalía; no certifica atribución personal.

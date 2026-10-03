"""Render an auditable comparison from completed-run receipts and manual review."""
from collections import Counter
from common import ROOT, read_json

metrics = read_json(ROOT / 'reports/luna-effort-metrics.json')
low, high = (metrics['runs'][key] for key in ['low', 'xhigh'])
low_eval = read_json(ROOT / 'reports/evaluation-luna.json')
high_eval = read_json(ROOT / 'reports/evaluation-luna-xhigh.json')
gold = read_json(ROOT / 'reference/gold.json')
ratios = metrics['comparison']
labels = {'faithful': 'Fiel', 'partial': 'Parcial', 'invalid': 'Incorrecto', 'missed': 'Omitido'}


def number(value, decimals=0):
    return f'{value:,.{decimals}f}'.replace(',', '_').replace('.', ',').replace('_', '.')


def duration(seconds):
    return f'{int(seconds // 60)} min {number(seconds % 60, 1)} s'


rows = [
    ('Casos fieles / 25', low['quality']['faithful'], high['quality']['faithful']),
    ('Casos parciales', low['quality']['partial'], high['quality']['partial']),
    ('Casos incorrectos dirigidos a la referencia', low['quality']['invalid'], high['quality']['invalid']),
    ('Casos omitidos', low['quality']['missed'], high['quality']['missed']),
    ('Registros guardados', low['savedCandidates'], high['savedCandidates']),
    ('Candidatos rechazados por el programa', low['rejectedCandidates'], high['rejectedCandidates']),
    ('Duplicados exactos', low['exactDuplicateRecords'], high['exactDuplicateRecords']),
    ('Operaciones del modelo', low['operations'], high['operations']),
]
for key, label in [
    ('input_tokens', 'Tokens de entrada'), ('cached_input_tokens', 'Entrada leída de caché'),
    ('output_tokens', 'Tokens de salida, incluido razonamiento'),
    ('reasoning_output_tokens', 'De la salida: tokens de razonamiento'),
    ('total_input_and_output_tokens', 'Total: entrada + salida'),
]:
    rows.append((label, low['usage'][key], high['usage'][key]))

text = [
    '# Luna low frente a xhigh · Vigo 23/12/2025', '',
    'Ensayo completado con GPT-5.6 Luna mediante la suscripción de ChatGPT y el cliente oficial Codex. '
    'Se reutilizaron la transcripción, los bloques, el esquema y las instrucciones del pase low. '
    'La referencia de 25 casos y seis controles permaneció congelada y fuera de las peticiones al modelo.', '',
    f"El resultado estricto pasa de **{low['quality']['faithful']}/25 a {high['quality']['faithful']}/25** casos fieles. "
    f"El pase xhigh usa **{number(ratios['totalTokensRatio'], 2)} veces** los tokens totales y tarda "
    f"**{number(ratios['elapsedTimeRatio'], 2)} veces** lo observado en low. "
    'Son resultados de una ejecución completada por esfuerzo, sin medición de la variación entre repeticiones.', '',
    '[Explorar xhigh con citas y audio](explorador-luna-xhigh.html) · '
    '[Explorar low](explorador-luna.html) · [Contadores conservados](luna-effort-metrics.json) · '
    '[Protocolo](../docs/comparacion-luna-xhigh.md)', '',
    '## Calidad, tiempo y consumo', '',
    '| Medida | Luna low | Luna xhigh |', '|---|---:|---:|',
]
text += [f'| {label} | {number(a)} | {number(b)} |' for label, a, b in rows]
text += [
    f"| Tiempo del pase completado | {duration(low['elapsedSeconds'])} | {duration(high['elapsedSeconds'])} |",
    f"| Equivalencia orientativa a precios API | {number(low['estimatedApiEquivalentUsd'], 6)} USD | {number(high['estimatedApiEquivalentUsd'], 6)} USD |", '',
    '**El razonamiento ya está incluido en la salida; no se suma otra vez al total.** '
    'Los tokens de entrada incluyen instrucciones, esquema y contexto repetido en cada operación. '
    'La referencia es una selección previa, no una anotación exhaustiva: estos resultados no miden precisión global '
    'ni certifican todos los registros guardados.', '',
    '## Intentos y límites del recuento', '',
    'El primer intento xhigh se interrumpió al alcanzar el límite local de 360 segundos en el primer bloque. '
    'No dejó respuesta final ni contador de uso. Tras inspeccionar el registro, se repitió con 900 segundos '
    'de margen por operación; los datos y parámetros de inferencia se mantuvieron. '
    'La tabla corresponde a ese segundo pase completado.', '',
    '**El consumo total de todos los intentos xhigh es desconocido**, porque falta el contador del intento interrumpido. '
    'No se le asigna un consumo de cero. También se excluyen del pase las comprobaciones mínimas de transporte: '
    'low, 2.481 de entrada y 25 de salida; xhigh, 2.483 de entrada y 60 de salida '
    '(33 de razonamiento incluidos). La comprobación xhigh duró 4,718 segundos y coincidió con '
    'la espera del primer bloque del pase completado. El trabajo del evaluador queda fuera de estos contadores.', '',
    '## Qué casos cambian', '',
    '| Caso | Afirmación de referencia | Low | Xhigh |', '|---|---|---|---|',
]
for g, a, b in zip(gold['cases'], low_eval['cases'], high_eval['cases'], strict=True):
    assert g['id'] == a['goldId'] == b['goldId']
    links = ' '.join(f'[{cid}](explorador-luna-xhigh.html#{cid})' for cid in b['claimReadingIds'])
    statement = g['expectedStatement'].replace('|', '/')
    text.append(f"| {g['id']} | {statement} | {labels[a['status']]} | {labels[b['status']]} {links} |")
text += ['', 'La [evaluación anotada](evaluation-luna-xhigh.json) explica cada decisión de xhigh y distingue '
    'lo que el modelo nunca generó de lo que el programa rechazó. Se mantiene la misma rúbrica: '
    'sujeto, valor, periodo, condiciones, modalidad y evidencia.', '', '## Errores observados', '']
for error in high_eval['observedErrors']:
    links = ' '.join(f'[{cid}](explorador-luna-xhigh.html#{cid})' for cid in error['claimReadingIds'])
    text.append(f"- **{error['id']}** {links}: {error['notes']}")
rejections = read_json(ROOT / 'runs' / high['experimentId'] / 'rejections.json')
counts = Counter(reason for rejected in rejections for reason in rejected['reasons'])
text += ['', 'Motivos de rechazo — pueden coincidir varios en un candidato: '
    + '; '.join(f'{key}: {value}' for key, value in sorted(counts.items())) + '.', '',
    '## Controles negativos', '']
for control in high_eval['negativeControls']:
    text.append(f"- **{control['goldId']}**: {control['notes']}")
text += ['', '## Precio de Luna', '',
    'La [ficha oficial de GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) '
    'publica estas tarifas estándar, comprobadas el 11 de septiembre de 2026:', '',
    '| Tipo | USD por millón de tokens |', '|---|---:|', '| Entrada | 0,20 |',
    '| Entrada leída de caché | 0,02 |', '| Salida | 1,20 |', '',
    'El esfuerzo de razonamiento no cambia la tarifa por token. Puede aumentar el consumo. '
    'Los [tokens de razonamiento se facturan como salida](https://developers.openai.com/api/docs/guides/reasoning). '
    'Estos ensayos utilizaron los límites de la suscripción: las equivalencias anteriores **no son cargos de API ni facturas**. '
    'No incluyen la transcripción, realizada una sola vez antes de los ensayos. '
    'Los contadores proceden de Codex y no de una petición comercial medida por API.', '',
    'No hubo lecturas ni escrituras de caché informadas. Las escrituras de caché tienen un multiplicador de 1,25 '
    'sobre la entrada normal; las peticiones de más de 272.000 tokens de entrada aplican multiplicadores adicionales. '
    'Los bloques utilizados están por debajo de ese umbral. Véase la '
    '[ficha de tarifas guardada](../docs/luna-pricing-2026-09-11.json).', '',
    '## Alcance', '',
    'Se evalúa fidelidad a la transcripción automática de una sesión pública, sin comprobar veracidad externa '
    'ni cotejar el audio caso por caso. La anomalía de diarización S0026–S0028 sigue presente en la fuente. '
    'La agrupación de asuntos no tiene una métrica exhaustiva de identidad en esta versión. '
    'La comparación no demuestra que xhigh siempre mejore ni justifica integrar automáticamente estas salidas '
    'en la aplicación.', '',
    'Las [comprobaciones sin nuevas inferencias](luna-xhigh-checks.json) verifican las entradas iniciales, '
    'las huellas de referencia y versiones, la reutilización de respuestas y la importación idempotente.', '',
]
(ROOT / 'reports/resultados-luna-xhigh.md').write_text('\n'.join(text), encoding='utf-8')
print({'report': 'reports/resultados-luna-xhigh.md', 'caseRows': len(gold['cases'])})

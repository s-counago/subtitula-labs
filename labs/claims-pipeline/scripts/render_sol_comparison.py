"""Compare preserved completed runs; never execute inference or rewrite old results."""
from collections import Counter
from datetime import datetime
from common import ROOT, read_json, write_json, now

config = read_json(ROOT / 'config/sol-experiment.json')
path = ROOT / 'runs' / config['experimentId']
manifest = read_json(path / 'manifest.json')
assert manifest['state'] in {'completed', 'completed_with_errors'}
receipts = [read_json(p) for p in sorted((path / 'receipts').glob('*.json'))]
assert all(r['state'] == 'completed' for r in receipts)
usage = dict(Counter())
for key in ['input_tokens', 'cached_input_tokens', 'cache_write_input_tokens',
            'output_tokens', 'reasoning_output_tokens']:
    usage[key] = sum(r['reportedCodexUsage'].get(key, 0) for r in receipts)
assert all(r['reportedCodexUsage']['input_tokens'] < 272000 for r in receipts)
assert usage['reasoning_output_tokens'] <= usage['output_tokens']
usage['total_input_and_output_tokens'] = usage['input_tokens'] + usage['output_tokens']
usage['non_reasoning_output_tokens'] = usage['output_tokens'] - usage['reasoning_output_tokens']
cost = ((usage['input_tokens'] - usage['cached_input_tokens'] - usage['cache_write_input_tokens'])
        * config['pricePerMillionInputTokens']
        + usage['cached_input_tokens'] * config['pricePerMillionCachedInputTokens']
        + usage['cache_write_input_tokens'] * config['pricePerMillionInputTokens'] * 1.25
        + usage['output_tokens'] * config['pricePerMillionOutputTokens']) / 1_000_000
evaluation = read_json(ROOT / 'reports/evaluation-sol.json')
counts = Counter(r['status'] for r in evaluation['cases'])
claims = read_json(path / 'claims.json')
blocks = read_json(path / 'blocks.json')
summary = read_json(path / 'summary.json')
assert round(cost, 9) == round(summary['apiPriceEquivalentUsd'], 9)
sol = {'experimentId': config['experimentId'], 'model': config['model'],
       'reasoningEffort': config['reasoningEffort'], 'state': manifest['state'],
       'operations': len(receipts), 'contextRounds': summary['contextRounds'],
       'usage': usage, 'elapsedSeconds': round((datetime.fromisoformat(manifest['finishedAt'])
        - datetime.fromisoformat(manifest['startedAt'])).total_seconds(), 3),
       'estimatedApiEquivalentUsd': round(cost, 9), 'apiEquivalentIsCharge': False,
       'quality': {key: counts.get(key, 0) for key in ['faithful', 'partial', 'invalid', 'missed']},
       'generatedCandidatesFinalPerBlock': sum(b.get('generatedCandidates', 0) for b in blocks),
       'savedCandidates': len(claims), 'rejectedCandidates': len(read_json(path / 'rejections.json')),
       'exactDuplicateRecords': len(claims) - len({(c['statement'], c['speakerId'],
        tuple(c['evidenceSegmentIds'])) for c in claims}),
       'operationsDetail': [{'stage': r['stage'], 'elapsedSeconds': r['elapsedSeconds'],
        'usage': r['reportedCodexUsage']} for r in receipts]}
previous = read_json(ROOT / 'reports/luna-effort-metrics.json')
runs = {'lunaLow': previous['runs']['low'], 'lunaXhigh': previous['runs']['xhigh'], 'solMedium': sol}
comparison = {key: {'additionalFaithfulCases': sol['quality']['faithful'] - r['quality']['faithful'],
    'totalTokensRatio': usage['total_input_and_output_tokens'] / r['usage']['total_input_and_output_tokens'],
    'elapsedTimeRatio': sol['elapsedSeconds'] / r['elapsedSeconds'],
    'apiEquivalentRatio': cost / r['estimatedApiEquivalentUsd']} for key, r in list(runs.items())[:2]}
write_json(ROOT / 'reports/sol-comparison-metrics.json', {'createdAt': now(), 'runs': runs,
    'comparisonSolAgainst': comparison, 'actualBilling': 'chatgpt_subscription_limits',
    'reasoningCounterIsSubsetOfOutput': True, 'apiPriceSources': [config['priceSource'], previous['apiPriceSource']],
    'interruptedAttempt': previous['interruptedAttempt'], 'auxiliaryProbes': previous['auxiliaryProbes'],
    'scope': 'Completed runs, including optional context. Excludes evaluator work, transcription, Luna probes and interrupted xhigh attempt.',
    'limitations': ['One completed run per configuration; no variance estimate.',
        'Reference recovery is not global output precision; reference is not exhaustive.',
        'All-attempt xhigh usage is unknown. API equivalents are not billed API charges.']})

def number(value, places=0):
    return f'{value:,.{places}f}'.replace(',', '_').replace('.', ',').replace('_', '.')

def duration(seconds):
    minutes, sec = divmod(seconds, 60)
    return f'{int(minutes)} min {number(sec, 1)} s'

columns = list(runs.values())
rows = [(label, [r['quality'][key] for r in columns]) for key, label in [
    ('faithful', 'Casos fieles / 25'), ('partial', 'Casos parciales'),
    ('invalid', 'Casos incorrectos dirigidos a la referencia'), ('missed', 'Casos omitidos')]]
rows += [(label, [r[key] for r in columns]) for key, label in [
    ('savedCandidates', 'Registros guardados'), ('rejectedCandidates', 'Candidatos rechazados'),
    ('exactDuplicateRecords', 'Duplicados exactos'), ('operations', 'Operaciones del modelo')]]
rows += [(label, [r['usage'][key] for r in columns]) for key, label in [
    ('input_tokens', 'Tokens de entrada'), ('cached_input_tokens', 'Entrada leída de caché'),
    ('output_tokens', 'Tokens de salida, incluido razonamiento'),
    ('reasoning_output_tokens', 'De la salida: razonamiento'),
    ('total_input_and_output_tokens', 'Total: entrada + salida')]]
report = ['# Sol medium frente a Luna low y xhigh · Vigo 23/12/2025', '',
    'Ensayo solicitado el 12 de septiembre de 2026: misma transcripción, tres bloques iniciales, '
    'instrucciones, esquemas, validadores y resolución de asuntos. Se cambió el modelo y el esfuerzo '
    'sin aplicar las mejoras propuestas. La referencia permaneció congelada y fuera de las peticiones.', '',
    f"Sol recupera **{counts['faithful']}/25 casos completos ({number(counts['faithful']/25*100)} %)**, "
    f"con {counts.get('partial', 0)} parciales y {counts.get('missed', 0)} omitidos. "
    'La misma medida dio 9/25 en Luna low y 12/25 en Luna xhigh. '
    '**Es recuperación de una selección previa, no precisión global de las salidas.**', '',
    '[Explorar Sol con citas y audio](explorador-sol.html) · [Evaluación anotada](evaluation-sol.json) · '
    '[Contadores](sol-comparison-metrics.json) · [Protocolo](../docs/comparacion-sol.md)', '',
    '## Comparación', '', '| Medida | Luna low | Luna xhigh | Sol medium |', '|---|---:|---:|---:|']
report += ['| ' + label + ' | ' + ' | '.join(number(v) for v in values) + ' |' for label, values in rows]
report += ['| Tiempo del pase completado | ' + ' | '.join(duration(r['elapsedSeconds']) for r in columns) + ' |',
    '| Equivalencia orientativa a precios API | ' + ' | '.join(number(r['estimatedApiEquivalentUsd'], 6) + ' USD' for r in columns) + ' |', '',
    '**El razonamiento ya está incluido en la salida; no se suma dos veces.** Los contadores incluyen '
    'instrucciones, esquema y contexto repetido. Se usaron los límites de la suscripción de ChatGPT; '
    'la equivalencia API no es un cargo ni una factura.', '',
    f"Sol realizó {summary['contextRounds']} ronda de contexto adicional, prevista por v1, sobre la frase ambigua "
    '«desa gama» del segundo bloque. La segunda extracción sustituye a la primera para validar y guardar; '
    'ambas operaciones y todos sus tokens se contabilizan. Los pases Luna no pidieron esa ronda. '
    f"Las extracciones finales por bloque generaron {sol['generatedCandidatesFinalPerBlock']} candidatos, "
    f"de los que se guardaron {len(claims)}. No hubo reintentos ni prueba de conexión separada en Sol.", '',
    'La tabla usa los pases completados. El primer intento xhigh terminó al alcanzar 360 segundos '
    'sin contador de uso; su consumo es desconocido y queda fuera. También se excluyen las pequeñas '
    'pruebas de transporte de Luna, conservadas en las métricas. Sol y xhigh completado tuvieron '
    'el mismo límite de espera de 900 segundos por operación; low tuvo 360. El trabajo del evaluador '
    'y la transcripción original no están incluidos.', '', '## Los 25 casos', '',
    '| Caso | Afirmación esperada | Luna low | Luna xhigh | Sol medium |', '|---|---|---|---|---|']
gold = read_json(ROOT / 'reference/gold.json')
evals = [read_json(ROOT / ('reports/' + file)) for file in ['evaluation-luna.json', 'evaluation-luna-xhigh.json', 'evaluation-sol.json']]
labels = {'faithful': 'Fiel', 'partial': 'Parcial', 'invalid': 'Incorrecto', 'missed': 'Omitido'}
for i, g in enumerate(gold['cases']):
    cases = [e['cases'][i] for e in evals]
    assert all(c['goldId'] == g['id'] for c in cases)
    links = ' '.join(f'[{cid}](explorador-sol.html#{cid})' for cid in cases[-1]['claimReadingIds'])
    report.append('| ' + g['id'] + ' | ' + g['expectedStatement'].replace('|', '/') + ' | '
                  + ' | '.join(labels[c['status']] for c in cases) + ' ' + links + ' |')
report += ['', 'Se mantienen los criterios de periodo, condiciones, modalidad, atomicidad y evidencia. '
    'Una aparición de otra voz o segmento no sustituye al caso esperado. La evaluación anotada '
    'explica las pérdidas durante generación o validación.', '', '## Errores observados en Sol', '']
for error in evaluation['observedErrors']:
    links = ' '.join(f'[{cid}](explorador-sol.html#{cid})' for cid in error['claimReadingIds'])
    report.append(f"- **{error['id']}** {links}: {error['notes']}")
reasons = Counter(reason for r in read_json(path / 'rejections.json') for reason in r['reasons'])
report += ['', 'Motivos de rechazo, con posible solapamiento: ' + ('; '.join(f'{k}: {v}' for k,v in sorted(reasons.items())) or 'ninguno') + '.', '',
    '## Controles negativos', '']
report += [f"- **{c['goldId']}**: {c['notes']}" for c in evaluation['negativeControls']]
report += ['', '## Precios y límites de la comparación', '',
    'Tarifas oficiales consultadas el 11–12 de septiembre de 2026: '
    '[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna), '
    '[Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol).', '',
    '| USD por millón de tokens | Luna | Sol |', '|---|---:|---:|',
    '| Entrada | 0,20 | 4,00 |', '| Entrada leída de caché | 0,02 | 0,40 |', '| Salida | 1,20 | 20,00 |', '',
    'Las escrituras de caché tienen un multiplicador de 1,25 sobre la entrada normal. '
    f"Sol informó de {number(usage['cached_input_tokens'])} tokens de entrada leídos de caché y ninguna escritura; "
    'ambos pases Luna informaron de cero lecturas y escrituras. Todas las operaciones están '
    'por debajo de 272.000 tokens de entrada. Los equivalentes utilizan contadores de Codex, '
    'no peticiones comerciales medidas por API.', '',
    'La revisión mide fidelidad a la transcripción de una única sesión. No verifica la verdad de '
    'las afirmaciones ni coteja el audio caso por caso. La referencia fue seleccionada inicialmente '
    'por Sol y revisada por el asistente principal antes de los ensayos; no constituye una evaluación '
    'humana independiente. La agrupación de asuntos tampoco tiene una métrica exhaustiva en v1. '
    'Una ejecución por configuración no permite medir variación ni generalizar estos porcentajes.', '',
    '[Comprobaciones sin inferencias nuevas](sol-checks.json): entradas iniciales iguales a GLM y '
    'ambos pases Luna, huellas conservadas, respuestas reutilizables, contadores verificados y '
    'doble importación sin duplicados.', '']
(ROOT / 'reports/resultados-sol.md').write_text('\n'.join(report), encoding='utf-8')
print({'sol': sol, 'comparisonSolAgainst': comparison})

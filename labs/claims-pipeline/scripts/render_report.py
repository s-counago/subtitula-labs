"""Readable, standalone local report. All source/model strings are escaped as text."""
import html
import json
import argparse
from common import ROOT, read_json

parser = argparse.ArgumentParser()
parser.add_argument('--config', default='config/experiment.json')
parser.add_argument('--suffix', default='')
parser.add_argument('--label', default='GLM')
parser.add_argument('--id-prefix', default='C')
options = parser.parse_args()
if options.suffix and not all(c.isalnum() or c == '-' for c in options.suffix):
    raise ValueError('Invalid report suffix')
config = read_json(ROOT / options.config)
run = ROOT / 'runs' / config['experimentId']
claims = read_json(run / 'claims.json')
matters = {m['id']: m for m in read_json(run / 'matters.json')}
summary = read_json(run / 'summary.json')
gold = read_json(ROOT / 'reference/gold.json')
evaluation_path = ROOT / ('reports/evaluation' + options.suffix + '.json')
evaluation = read_json(evaluation_path) if evaluation_path.exists() else None
claim_ids = {c['claimId']: f'{options.id_prefix}{i:03d}' for i, c in enumerate(claims, 1)}
write_map = {short: full for full, short in claim_ids.items()}
(run / 'reading-ids.json').write_text(json.dumps(write_map, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def tc(t):
    seconds = int(t)
    return f'{seconds//60:02d}:{seconds%60:02d}'

def esc(value):
    return html.escape(str(value) if value is not None else 'Sin concretar')

labels = {'asserted_fact': 'Hecho afirmado', 'proposal': 'Propuesta', 'commitment': 'Compromiso',
          'reported_statement': 'Declaración referida', 'opinion': 'Opinión'}
cards = []
markdown = ['# Hallazgos de GLM · Vigo 23/12/2025', '',
            'Propuestas extraídas de una transcripción automática. No se ha comprobado su veracidad ni la identidad de las voces.', '',
            f"{len(claims)} registros candidatos con validación estructural y de citas; {len(matters)} asuntos propuestos. Incluyen duplicados y errores semánticos conservados para el ensayo.", '']
for c in claims:
    cid = claim_ids[c['claimId']]
    matter = matters.get(c['canonicalMatterId'], {}).get('label', 'Asunto pendiente')
    details = [('Voz', c['speakerId']), ('Tipo', labels[c['modality']]), ('Periodo', c['referencePeriod']),
               ('Valor', c['valueText']), ('Propiedad', c['property'])]
    dl = ''.join(f'<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>' for k, v in details)
    conditions = ' · '.join(c['conditions']) or 'Sin condiciones adicionales registradas'
    annotations = []
    if evaluation:
        annotations += [r['goldId'] + ': ' + r['notes'] for r in evaluation['cases'] if cid in r.get('claimReadingIds', [])]
        annotations += [r['id'] + ': ' + r['notes'] for r in evaluation['observedErrors'] if cid in r.get('claimReadingIds', [])]
    review_html = ''.join('<p class="notice"><strong>Revisión:</strong> ' + esc(note) + '</p>' for note in annotations)
    search = ' '.join([c['statement'], matter, c['quote'], conditions]).casefold()
    cards.append(f'''<article class="claim" id="{cid}" data-speaker="{esc(c['speakerId'])}" data-matter="{esc(c['canonicalMatterId'])}" data-search="{esc(search)}">
<div class="eyebrow">{cid} · {tc(c['start'])}–{tc(c['end'])} · salida original de v1</div>
<h3>{esc(c['statement'])}</h3>{review_html}<p class="matter">{esc(matter)}</p><dl>{dl}</dl>
<p class="conditions">{esc(conditions)}</p><blockquote>{esc(c['quote'])}</blockquote>
<p class="source">Segmentos: {esc(', '.join(c['evidenceSegmentIds']))} · Contexto: {esc(', '.join(c['contextSegmentIds']) or '—')}</p>
<button class="listen" data-start="{c['start']}">Escuchar desde {tc(c['start'])}</button>
<details><summary>Identificadores y observaciones</summary><p>{esc(c['claimId'])}</p><p>{esc(c.get('uncertainty'))}</p></details></article>''')
    markdown += [f'## {cid} · {tc(c["start"])} · {c["speakerId"]}', '', c['statement'], '',
                 f'**Asunto:** {matter}. **Modalidad:** {labels[c["modality"]]}.', '',
                 f'**Periodo:** {c["referencePeriod"] or "Sin concretar"}. **Valor:** {c["valueText"] or "Sin concretar"}.', '',
                 f'**Condiciones:** {conditions}', '', '> ' + c['quote'], '',
                 'Segmentos: ' + ', '.join(c['evidenceSegmentIds']) + '. Contexto: ' + (', '.join(c['contextSegmentIds']) or '—'), '',
                 f'Identidad: `{c["claimId"]}`.', '']

rows = []
results = {r['goldId']: r for r in evaluation['cases']} if evaluation else {}
status_labels = {'faithful': 'Fiel', 'partial': 'Parcial', 'missed': 'Omitido', 'invalid': 'Incorrecto'}
for g in gold['cases']:
    result = results.get(g['id'])
    state = status_labels.get(result['status'], result['status']) if result else 'Pendiente de comparar'
    matches = ' '.join(f'<a href="#{esc(cid)}">{esc(cid)}</a>' for cid in result.get('claimReadingIds', [])) if result else ''
    note = result['notes'] if result else ''
    rows.append(f'<tr><td>{esc(g["id"])}</td><td>{esc(g["expectedStatement"])}</td><td>{esc(state)} {matches}<small>{esc(note)}</small></td></tr>')

speakers = ''.join(f'<option>{esc(s)}</option>' for s in sorted({c['speakerId'] for c in claims}))
matter_options = ''.join(f'<option value="{esc(m["id"])}">{esc(m["label"])}</option>' for m in matters.values())
if any(c['canonicalMatterId'] is None for c in claims):
    matter_options += '<option value="Sin concretar">Asunto pendiente</option>'
result_text = 'La comparación está pendiente.'
if evaluation:
    counts = {k: sum(r['status'] == k for r in evaluation['cases']) for k in status_labels}
    result_text = f"Referencia de 25 casos: {counts['faithful']} fieles, {counts['partial']} parciales, {counts['missed']} omitidos, {counts['invalid']} incorrectos."

page = '''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Laboratorio de afirmaciones · Vigo</title><style>
:root{color-scheme:light;--ink:#16312c;--muted:#526b65;--line:#d3dfda;--accent:#1b6b55;--paper:#f5f7f3}*{box-sizing:border-box}body{margin:0;background:var(--paper);font:16px/1.55 system-ui,sans-serif;color:var(--ink)}main{max-width:1150px;margin:auto;padding:44px 28px}h1{font-size:clamp(30px,4vw,48px);line-height:1.1;max-width:900px;margin:10px 0 18px}h2{font-size:27px;margin-top:40px}h3{font-size:20px;line-height:1.4;margin:8px 0}p{max-width:900px}a{color:var(--accent)}.eyebrow{text-transform:uppercase;letter-spacing:.08em;font-size:12px;color:var(--muted)}.intro{font-size:19px}.stats{display:flex;gap:12px;flex-wrap:wrap;margin:25px 0}.stat{background:#fff;border:1px solid var(--line);border-radius:12px;padding:15px 20px;min-width:150px}.stat b{display:block;font-size:27px}.notice{padding:18px 22px;border-left:4px solid #b98727;background:#fff8e8}.toolbar{display:flex;gap:12px;flex-wrap:wrap;padding:14px;background:#e5eee7;border-radius:12px}label{display:flex;flex-direction:column;font-size:13px;gap:5px}label:first-child{flex:1;min-width:240px}input,select{font:inherit;font-size:15px;padding:11px;border:1px solid #91aaa0;border-radius:7px;max-width:400px;width:100%}input{max-width:none}.claim{background:#fff;border:1px solid var(--line);border-radius:14px;padding:25px;margin:18px 0;scroll-margin-top:20px}.claim[hidden]{display:none}.matter{color:var(--accent);font-weight:650}dl{display:flex;gap:15px 25px;flex-wrap:wrap}dl div{max-width:100%}dt{font-size:12px;text-transform:uppercase;color:var(--muted)}dd{margin:3px 0;overflow-wrap:anywhere;font-size:14px}.conditions,.source{font-size:14px;color:var(--muted)}blockquote{border-left:3px solid #a2b9ab;margin:20px 0;padding:8px 18px;background:#f5f8f4}button{font:inherit;font-size:14px;padding:9px 14px;border:0;border-radius:7px;background:var(--accent);color:white;cursor:pointer}details{margin-top:13px;font-size:13px;overflow-wrap:anywhere}audio{width:100%;max-width:720px}.reference{overflow:auto}table{border-collapse:collapse;width:100%;background:white;font-size:14px}td,th{padding:13px;text-align:left;vertical-align:top;border:1px solid var(--line)}td:first-child{white-space:nowrap}small{display:block;color:var(--muted);margin-top:6px}footer{margin-top:36px;font-size:13px;color:var(--muted)}@media(max-width:600px){main{padding:25px 16px}.claim{padding:19px}.toolbar{display:block}.toolbar label{margin-bottom:10px}.stat{min-width:120px}}
</style></head><body><main><div class="eyebrow">Ensayo local · 11 de septiembre de 2026</div>
<h1>Qué encuentra GLM en un pleno de Vigo</h1><p class="intro">Grabación completa del 23 de diciembre de 2025: 26:55 sobre el presupuesto de 2026. La referencia se revisó y congeló antes de ejecutar el modelo.</p>
<div class="stats"><div class="stat"><b>__CLAIMS__</b>registros candidatos</div><div class="stat"><b>__MATTERS__</b>asuntos propuestos</div><div class="stat"><b>25 + 6</b>casos y controles previos</div><div class="stat"><b>__COST__ USD</b>generación estimada</div></div>
<p class="notice">Se evalúa fidelidad a una transcripción automática. Las cifras y opiniones siguen atribuidas a sus hablantes y no se han contrastado. S0026–S0028 presentan una anomalía de diarización: las etiquetas de voz no acreditan identidades personales.</p>
<p>__RESULT__ <a href="resultados.md">Leer el informe</a> · <a href="#comparison">Ver los 25 casos</a> · <a href="../docs/pipeline.md">Diagrama y pseudocódigo</a> · <a href="https://mediateca.vigo.org/library/items/122">Grabación oficial</a></p>
<h2>Escuchar y explorar los hallazgos</h2><audio id="audio" controls preload="none" src="../inputs/media/vigo-2025-12-23.mp3"></audio><p id="audio-status" class="source">Los tiempos son relativos a la grabación.</p>
<div class="toolbar"><label>Buscar en afirmaciones y citas<input id="query" type="search" placeholder="Presupuesto, vivienda, 2025…"></label><label>Voz<select id="speaker"><option value="">Todas las voces</option>__SPEAKERS__</select></label><label>Asunto<select id="matter"><option value="">Todos los asuntos</option>__MATTER_OPTIONS__</select></label></div>
<p id="count" class="source"></p><section id="claims">__CARDS__</section>
<h2 id="comparison">Comparación con la referencia congelada</h2><p>Los 25 ejemplos son una selección previa, no una anotación exhaustiva del pleno. Los resultados no expresan precisión global.</p><div class="reference"><table><thead><tr><th>Caso</th><th>Afirmación esperada</th><th>Revisión</th></tr></thead><tbody>__ROWS__</tbody></table></div>
<footer>GLM-4.7-Flash · ElevenLabs Scribe v2 · propuestas locales. El coste mostrado deriva de tokens informados y tarifa de catálogo; no es una factura. Audio: 1.795 créditos informados por ElevenLabs.</footer></main>
<script>
const cards=[...document.querySelectorAll('.claim')],query=document.querySelector('#query'),speaker=document.querySelector('#speaker'),matter=document.querySelector('#matter'),count=document.querySelector('#count'),audio=document.querySelector('#audio');
function filter(){let n=0;const q=query.value.toLocaleLowerCase();for(const card of cards){const show=(!q||card.dataset.search.includes(q))&&(!speaker.value||card.dataset.speaker===speaker.value)&&(!matter.value||card.dataset.matter===matter.value);card.hidden=!show;if(show)n++;}count.textContent=n+' de '+cards.length+' registros visibles';}
for(const field of [query,speaker,matter])field.addEventListener('input',filter);filter();
for(const button of document.querySelectorAll('.listen'))button.addEventListener('click',async()=>{const status=document.querySelector('#audio-status');try{if(audio.readyState===0){status.textContent='Cargando el audio local…';audio.preload='metadata';await new Promise((resolve,reject)=>{audio.addEventListener('loadedmetadata',resolve,{once:true});audio.addEventListener('error',reject,{once:true});audio.load();});}audio.currentTime=Number(button.dataset.start);await audio.play();status.textContent='Escuchando desde '+button.textContent.replace('Escuchar desde ','');}catch{status.textContent='Pulsa reproducir en el control de audio o comprueba que el archivo local sigue disponible.';}});
for(const a of document.querySelectorAll('a[href^="#C"]'))a.addEventListener('click',()=>{query.value='';speaker.value='';matter.value='';filter();});
</script></body></html>'''
if options.label != 'GLM':
    page = page.replace('Qué encuentra GLM', 'Qué encuentra ' + esc(options.label))
    page = page.replace('GLM-4.7-Flash', esc(config['model']))
    page = page.replace('resultados.md', 'resultados' + options.suffix + '.md')
    page = page.replace('a[href^="#C"]', 'a[href^="#' + options.id_prefix + '"]')
    markdown[0] = '# Hallazgos de ' + options.label + ' · Vigo 23/12/2025'
if summary.get('billing') == 'chatgpt_subscription_limits':
    page = page.replace('__COST__ USD</b>generación estimada', 'Suscripción</b>límites de ChatGPT')
    page = page.replace('El coste mostrado deriva de tokens informados y tarifa de catálogo; no es una factura.',
        'Este pase usa la suscripción mediante Codex. Se conserva el mismo audio sin repetir la transcripción.')
cost_text = f"{summary.get('estimatedGenerationCostUsdFromReportedTokens', 0):.5f}"
for key, value in {'__CLAIMS__': str(len(claims)), '__MATTERS__': str(len(matters)),
    '__COST__': cost_text, '__RESULT__': esc(result_text),
    '__SPEAKERS__': speakers, '__MATTER_OPTIONS__': matter_options, '__CARDS__': '\n'.join(cards), '__ROWS__': '\n'.join(rows)}.items():
    page = page.replace(key, value)
(ROOT / ('reports/explorador' + options.suffix + '.html')).write_text(page, encoding='utf-8')
(ROOT / ('reports/hallazgos' + options.suffix + '.md')).write_text('\n'.join(markdown), encoding='utf-8')
print({'cards': len(cards), 'referenceRows': len(rows), 'suffix': options.suffix})

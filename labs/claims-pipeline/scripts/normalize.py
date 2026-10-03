"""Turn Scribe words into short, stable, same-speaker segments without LLM rewriting."""
from common import ROOT, read_json, write_json, sha, now

source = ROOT / 'inputs/transcripts/scribe-v2.json'
raw = read_json(source)
digest = sha(source)
segments = []
pending = []

def flush():
    if not pending:
        return
    text = ''.join(w['text'] for w in pending).strip()
    if text:
        segments.append({'id': f'S{len(segments)+1:04d}', 'sequence': len(segments)+1,
                         'start': pending[0]['start'], 'end': pending[-1]['end'],
                         'speakerId': pending[0].get('speaker_id') or 'unknown', 'text': text,
                         'transcriptSha256': digest})
    pending.clear()

for word in raw.get('words', []):
    if word.get('type') == 'audio_event':
        flush()
        continue
    if word.get('type') == 'spacing':
        if pending:
            pending.append(word)
        continue
    if word.get('type') != 'word':
        continue
    if pending:
        speech = [w for w in pending if w.get('type') == 'word']
        if (word.get('speaker_id') != speech[-1].get('speaker_id') or
                word['start'] - speech[-1]['end'] > 2.0 or
                (len(''.join(w['text'] for w in pending)) > 450 and
                 speech[-1]['text'].rstrip().endswith(('.', '?', '!', ';')) ) or
                len(''.join(w['text'] for w in pending)) > 850):
            flush()
    pending.append(word)
flush()

write_json(ROOT / 'inputs/transcripts/segments.json', {'createdAt': now(), 'sourceSha256': digest,
    'normalizerVersion': '1.0', 'sourceLanguage': raw.get('language_code'), 'segments': segments})

def tc(t):
    seconds = int(t)
    return f'{seconds//3600:02d}:{seconds//60%60:02d}:{seconds%60:02d}'

lines = ['# Transcripción del pleno de Vigo · 23 de diciembre de 2025', '',
         'Salida de Scribe v2; etiquetas de voz sin identidad personal verificada. No se corrige el contenido.', '']
for s in segments:
    lines += [f"## {s['id']} · {tc(s['start'])}–{tc(s['end'])} · {s['speakerId']}", '', s['text'], '']
(ROOT / 'inputs/transcripts/transcript.md').write_text('\n'.join(lines), encoding='utf-8')
print({'segments': len(segments), 'wordCount': sum(w.get('type') == 'word' for w in raw['words']),
       'speakers': sorted({s['speakerId'] for s in segments}), 'lastEndSeconds': segments[-1]['end']})

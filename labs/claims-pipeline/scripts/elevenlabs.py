"""Explicit single-shot transcription; read-only subscription check. No automatic paid retries."""
import argparse
import time
import requests
from common import ROOT, eleven_key, now, sha, write_json

parser = argparse.ArgumentParser()
parser.add_argument('action', choices=['quota', 'transcribe'])
parser.add_argument('--env-file')
parser.add_argument('--audio')
parser.add_argument('--language', default='glg')
args = parser.parse_args()
headers = {'xi-api-key': eleven_key(args.env_file)}

def quota():
    r = requests.get('https://api.elevenlabs.io/v1/user/subscription', headers=headers, timeout=30)
    data = r.json()
    safe = {'checkedAt': now(), 'httpStatus': r.status_code}
    if r.ok:
        for key in ['tier', 'status', 'character_count', 'character_limit', 'can_extend_character_limit', 'next_character_count_reset_unix']:
            safe[key] = data.get(key)
    else:
        detail = data.get('detail', {})
        safe['errorCode'] = detail.get('status') if isinstance(detail, dict) else 'request_failed'
    return safe

if args.action == 'quota':
    result = quota()
    write_json(ROOT / 'reports/elevenlabs-quota-before.json', result)
    print(result)
else:
    audio = ROOT / args.audio
    output = ROOT / 'inputs/transcripts/scribe-v2.json'
    receipt_path = ROOT / 'inputs/transcripts/transcription-receipt.json'
    if output.exists() or receipt_path.exists():
        raise SystemExit('An output or receipt already exists. Inspect it before any new paid request.')
    options = {'model_id': 'scribe_v2', 'language_code': args.language, 'diarize': 'true',
               'timestamps_granularity': 'word', 'tag_audio_events': 'true', 'webhook': 'false',
               'use_speaker_library': 'false'}
    receipt = {'startedAt': now(), 'audioPath': str(audio.relative_to(ROOT)), 'audioSha256': sha(audio),
               'options': options, 'state': 'sending', 'automaticRetries': 0}
    write_json(receipt_path, receipt)
    start = time.monotonic()
    try:
        with audio.open('rb') as f:
            r = requests.post('https://api.elevenlabs.io/v1/speech-to-text', headers=headers,
                              data=options, files={'file': (audio.name, f, 'audio/mpeg')}, timeout=(30, 900))
        receipt.update({'httpStatus': r.status_code, 'finishedAt': now(), 'elapsedSeconds': round(time.monotonic() - start, 2),
                        'requestId': r.headers.get('request-id'), 'characterCostHeader': r.headers.get('character-cost')})
        data = r.json()
        if r.ok:
            write_json(output, data)
            receipt.update({'state': 'completed', 'outputSha256': sha(output), 'words': len(data.get('words', []))})
        else:
            detail = data.get('detail', {})
            receipt.update({'state': 'failed', 'errorCode': detail.get('status') if isinstance(detail, dict) else 'request_failed'})
        write_json(receipt_path, receipt)
        print({k: receipt[k] for k in ['state', 'httpStatus', 'elapsedSeconds']})
        if not r.ok:
            raise SystemExit('Transcription failed; no automatic retry.')
        write_json(ROOT / 'reports/elevenlabs-quota-after.json', quota())
    except requests.RequestException as error:
        receipt.update({'state': 'uncertain', 'finishedAt': now(), 'errorType': type(error).__name__})
        write_json(receipt_path, receipt)
        raise SystemExit('Network result uncertain; inspect provider before attempting another paid request.')

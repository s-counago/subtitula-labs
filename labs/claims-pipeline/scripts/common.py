"""Local laboratory helpers. Never print credentials or request headers."""
from pathlib import Path
import hashlib
import json
import os
import re
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]

def now():
    return datetime.now(timezone.utc).isoformat()

def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def eleven_key(env_file=None):
    if os.environ.get('ELEVENLABS_API_KEY'):
        return os.environ['ELEVENLABS_API_KEY']
    if env_file:
        values = Path(env_file).read_text(encoding='utf-8-sig')
        match = re.search(r'^ELEVENLABS_API_KEY\s*=\s*(.+)$', values, re.M)
        if match:
            return match[1].strip().strip('"').strip("'")
    raise RuntimeError('ElevenLabs credential unavailable; supply an environment variable or private env-file path.')

def cloudflare_key():
    if os.environ.get('CLOUDFLARE_API_TOKEN'):
        return os.environ['CLOUDFLARE_API_TOKEN']
    path = Path(os.environ['APPDATA']) / 'xdg.config/.wrangler/config/default.toml'
    match = re.search(r'^oauth_token\s*=\s*"([^"]+)"', path.read_text(encoding='utf-8'), re.M)
    if not match:
        raise RuntimeError('Cloudflare authenticated session unavailable.')
    return match[1]

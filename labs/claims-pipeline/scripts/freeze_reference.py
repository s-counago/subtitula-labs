"""Freeze the reviewed reference BEFORE any paid GLM requests; never pass cases to the model."""
from common import ROOT, read_json, write_json, sha, now
from contracts import normalize_space

source = ROOT / 'reference/gold-draft.json'
target = ROOT / 'reference/gold.json'
manifest = ROOT / 'reference/frozen.json'
if manifest.exists() or target.exists():
    raise SystemExit('Reference already frozen. Preserve it and create another experiment for changes.')
if list((ROOT / 'runs').glob('*/responses/*.json')) or list((ROOT / 'runs').glob('*/receipts/*.json')):
    raise SystemExit('Cannot create a pre-inference reference after inference has started.')
reference = read_json(source)
segments = read_json(ROOT / 'inputs/transcripts/segments.json')['segments']
by_id = {s['id']: s for s in segments}
assert 20 <= len(reference['cases']) <= 30
assert len({c['id'] for c in reference['cases']}) == len(reference['cases'])
for c in reference['cases'] + reference.get('negativeControls', []):
    evidence = [by_id[key] for key in c['evidenceSegmentIds']]
    assert normalize_space(c['quote']) in normalize_space(' '.join(s['text'] for s in evidence)), c['id']
    if 'speakerId' in c:
        assert all(s['speakerId'] == c['speakerId'] for s in evidence), c['id']
write_json(target, reference)
write_json(manifest, {'frozenAt': now(), 'referencePath': 'reference/gold.json', 'referenceSha256': sha(target),
    'transcriptSha256': sha(ROOT / 'inputs/transcripts/scribe-v2.json'),
    'segmentsSha256': sha(ROOT / 'inputs/transcripts/segments.json'),
    'reviewNotesSha256': sha(ROOT / 'reference/review-notes.md'),
    'positiveCases': len(reference['cases']), 'negativeControls': len(reference.get('negativeControls', [])),
    'reviewers': ['gpt-5.6-sol', 'root assistant'], 'basis': 'transcript_only',
    'glmRequestsAtFreeze': 0, 'exhaustiveAnnotation': False})
print({'frozen': True, 'cases': len(reference['cases']), 'referenceSha256': sha(target)})

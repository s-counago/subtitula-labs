"""Offline checks of comparison inputs, preserved baseline and replay idempotency."""
import json
import argparse
from collections import Counter
from pathlib import Path
from unittest.mock import patch
from common import ROOT, read_json, sha, write_json, now
from contracts import EXTRACTION_SCHEMA, RESOLUTION_SCHEMA, validate_shape
from luna_pipeline import CodexRunner

parser = argparse.ArgumentParser()
parser.add_argument('--config', default='config/luna-experiment.json')
parser.add_argument('--suffix', default='-luna')
parser.add_argument('--id-prefix', default='L')
options = parser.parse_args()
assert all(c.isalnum() or c == '-' for c in options.suffix)
config = read_json(ROOT / options.config)
run = ROOT / 'runs' / config['experimentId']
baseline = ROOT / 'runs/vigo-2025-12-23-v1'
original_config = read_json(ROOT / 'config/experiment.json')
frozen = read_json(ROOT / 'reference/frozen.json')
for path, field in [('reference/gold.json', 'referenceSha256'),
    ('inputs/transcripts/scribe-v2.json', 'transcriptSha256'),
    ('inputs/transcripts/segments.json', 'segmentsSha256')]:
    assert sha(ROOT / path) == frozen[field], path
low_run = ROOT / 'runs/vigo-2025-12-23-luna-v1'
for manifest_path in set([baseline / 'manifest.json', low_run / 'manifest.json', run / 'manifest.json']):
    manifest = read_json(manifest_path)
    for path, expected in {**manifest['inputHashes'], **manifest.get('adapterHashes', {}), **manifest.get('variantHashes', {})}.items():
        assert sha(ROOT / path) == expected, path
    assert manifest['referenceSha256'] == frozen['referenceSha256']
for key in ['sessionId', 'institution', 'territory', 'sessionDate', 'agenda',
    'maxBlockCharacters', 'neighborSegments', 'maxContextRounds', 'maxContextRequests', 'maxContextCharacters']:
    assert config[key] == original_config[key], key
equal_payloads = []
for i in range(1, 4):
    stage = f'block-{i:02d}-extract'
    glm = read_json(baseline / 'requests' / (stage + '.json'))
    luna = read_json(run / 'requests' / (stage + '.json'))
    assert luna['instructions'] == glm['messages'][0]['content']
    assert luna['payload'] == json.loads(glm['messages'][1]['content'])
    assert luna['schema'] == glm['response_format']['json_schema']['schema']
    low_request = read_json(low_run / 'requests' / (stage + '.json'))
    assert luna['instructions'] == low_request['instructions']
    assert luna['payload'] == low_request['payload']
    assert luna['schema'] == low_request['schema']
    equal_payloads.append(stage)

protected_paths = [run / 'manifest.json', baseline / 'manifest.json', low_run / 'manifest.json', ROOT / 'reference/gold.json']
protected_paths += list((run / 'responses').glob('*.json'))
protected_paths += list((baseline / 'responses').glob('*.json'))
protected_paths += list((low_run / 'responses').glob('*.json'))
before_hashes = {str(path): sha(path) for path in protected_paths}
runner = CodexRunner.__new__(CodexRunner)
runner.config = config
runner.path = run
replayed = []
with patch('luna_pipeline.run_codex', side_effect=RuntimeError('Inference prohibited in verification')):
    for path in sorted((run / 'requests').glob('*.json')):
        request = read_json(path)
        runner.infer(path.stem, request['instructions'], request['payload'], request['schema'])
        replayed.append(path.stem)
for key, attribute in [('claims', 'claims'), ('matters', 'catalog'), ('mentions', 'mentions'),
    ('rejections', 'rejections'), ('blocks', 'blocks')]:
    setattr(runner, attribute, read_json(run / (key + '.json')))
runner.path = ROOT / ('reports/replay' + options.suffix + '-check')
runner.path.mkdir(parents=True, exist_ok=True)
first = runner.persist()['counts']
second = runner.persist()['counts']
assert first == second == read_json(run / 'summary.json')['counts']
assert before_hashes == {str(path): sha(path) for path in protected_paths}

evaluation = read_json(ROOT / ('reports/evaluation' + options.suffix + '.json'))
gold = read_json(ROOT / 'reference/gold.json')
assert [case['goldId'] for case in evaluation['cases']] == [case['id'] for case in gold['cases']]
valid_ids = {f'{options.id_prefix}{i:03d}' for i in range(1, len(runner.claims) + 1)}
for row in evaluation['cases'] + evaluation['negativeControls'] + evaluation['observedErrors']:
    assert not set(row['claimReadingIds']) - valid_ids
counts = dict(Counter(case['status'] for case in evaluation['cases']))
duplicates = len(runner.claims) - len({(c['statement'], c['speakerId'], tuple(c['evidenceSegmentIds'])) for c in runner.claims})
tool_items = []
for path in (run / 'transport').glob('*/events.jsonl'):
    for line in path.read_text(encoding='utf-8').splitlines():
        event = json.loads(line)
        if event.get('type', '').startswith('item.') and event.get('item', {}).get('type') not in {'error', 'agent_message', 'reasoning'}:
            tool_items.append(event)
assert not tool_items
write_json(ROOT / ('reports/' + options.suffix.lstrip('-') + '-checks.json'), {'checkedAt': now(), 'result': 'passed',
    'initialExtractionPayloadsEqualToGlm': equal_payloads,
    'initialExtractionPayloadsEqualToLunaLow': equal_payloads,
    'unchangedBaselineAndReference': True, 'cachedResponsesReplayed': len(replayed),
    'newModelCalls': 0, 'databaseCountsAfterFirstImport': first,
    'databaseCountsAfterSecondImport': second, 'unexpectedToolItems': len(tool_items),
    'evaluationCounts': counts, 'exactDuplicateRecords': duplicates})
print(json.dumps({'result': 'passed', 'cachedResponsesReplayed': len(replayed),
    'newModelCalls': 0, 'evaluationCounts': counts, 'exactDuplicateRecords': duplicates}, ensure_ascii=False))

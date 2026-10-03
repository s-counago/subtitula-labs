"""Offline evidence that the Sol experiment preserved the v1 process and baselines."""
import json
from collections import Counter
from unittest.mock import patch
from common import ROOT, read_json, write_json, sha, now
from pipeline import Runner
from luna_pipeline import CodexRunner
from sol_pipeline import SolRunner

config = read_json(ROOT / 'config/sol-experiment.json')
run = ROOT / 'runs' / config['experimentId']
assert read_json(run / 'manifest.json')['state'] in {'completed', 'completed_with_errors'}
assert SolRunner.infer is CodexRunner.infer and SolRunner.resolve is Runner.resolve
snapshot = read_json(run / 'comparison-baseline-hashes.json')
for name, digest in snapshot['hashes'].items():
    assert sha(ROOT / name) == digest, name

baselines = [ROOT / 'runs' / name for name in [
    'vigo-2025-12-23-v1', 'vigo-2025-12-23-luna-v1', 'vigo-2025-12-23-luna-xhigh-v1b']]
for path in baselines + [run]:
    manifest = read_json(path / 'manifest.json')
    for name, digest in {**manifest['inputHashes'], **manifest.get('adapterHashes', {}),
                         **manifest.get('variantHashes', {})}.items():
        assert sha(ROOT / name) == digest, name
for i in range(1, 4):
    name = f'block-{i:02d}-extract.json'
    actual = read_json(run / 'requests' / name)
    for baseline in baselines[1:]:
        previous = read_json(baseline / 'requests' / name)
        assert all(actual[k] == previous[k] for k in ['instructions', 'payload', 'schema'])
    original = read_json(baselines[0] / 'requests' / name)
    assert actual['instructions'] == original['messages'][0]['content']
    assert actual['payload'] == json.loads(original['messages'][1]['content'])
    assert actual['schema'] == original['response_format']['json_schema']['schema']

protected = [run / 'manifest.json', *list((run / 'responses').glob('*.json'))]
before = {str(path): sha(path) for path in protected}
runner = SolRunner.__new__(SolRunner)
runner.config, runner.path = config, run
replayed = []
with patch('luna_pipeline.run_codex', side_effect=RuntimeError('No new inference permitted')):
    for path in sorted((run / 'requests').glob('*.json')):
        req = read_json(path)
        assert req['model'] == 'gpt-5.6-sol' and req['reasoningEffort'] == 'medium'
        runner.infer(path.stem, req['instructions'], req['payload'], req['schema'])
        replayed.append(path.stem)
for file, attribute in [('claims', 'claims'), ('matters', 'catalog'), ('mentions', 'mentions'),
                         ('rejections', 'rejections'), ('blocks', 'blocks')]:
    setattr(runner, attribute, read_json(run / (file + '.json')))
runner.path = ROOT / 'reports/replay-sol-check'
runner.path.mkdir(parents=True, exist_ok=True)
first, second = runner.persist()['counts'], runner.persist()['counts']
assert first == second == read_json(run / 'summary.json')['counts']
assert before == {str(path): sha(path) for path in protected}

usage = Counter()
for path in (run / 'receipts').glob('*.json'):
    receipt = read_json(path)
    assert receipt['state'] == 'completed'
    events_path = run / 'transport' / receipt['stage'] / 'events.jsonl'
    assert sha(events_path) == receipt['eventsSha256']
    events = [json.loads(line) for line in events_path.read_text(encoding='utf-8').splitlines()]
    completed = [e for e in events if e.get('type') == 'turn.completed']
    assert len(completed) == 1 and completed[0]['usage'] == receipt['reportedCodexUsage']
    assert not [e for e in events if e.get('type', '').startswith('item.') and
                e.get('item', {}).get('type') not in {'error', 'agent_message', 'reasoning'}]
    usage.update(receipt['reportedCodexUsage'])
    assert usage['reasoning_output_tokens'] <= usage['output_tokens']
assert usage['input_tokens'] == read_json(run / 'summary.json')['reportedCodexUsage']['input_tokens']
assert usage['output_tokens'] == read_json(run / 'summary.json')['reportedCodexUsage']['output_tokens']
evaluation = read_json(ROOT / 'reports/evaluation-sol.json')
gold = read_json(ROOT / 'reference/gold.json')
assert [r['goldId'] for r in evaluation['cases']] == [r['id'] for r in gold['cases']]
assert [r['goldId'] for r in evaluation['negativeControls']] == [r['id'] for r in gold['negativeControls']]
valid_ids = {f'S{i:03d}' for i in range(1, len(runner.claims) + 1)}
for row in evaluation['cases'] + evaluation['negativeControls'] + evaluation['observedErrors']:
    assert not set(row['claimReadingIds']) - valid_ids
duplicates = len(runner.claims) - len({(c['statement'], c['speakerId'], tuple(c['evidenceSegmentIds']))
                                     for c in runner.claims})
result = {'checkedAt': now(), 'result': 'passed', 'generationMethodsInheritedUnchanged': True,
    'allThreeInitialPayloadsEqualToGlmAndBothLunaRuns': True,
    'baselineFilesUnchanged': len(snapshot['hashes']), 'cachedResponsesReplayed': len(replayed),
    'newModelCalls': 0, 'databaseCountsAfterFirstImport': first, 'databaseCountsAfterSecondImport': second,
    'receiptCountersMatchCompletionEvents': True, 'unexpectedToolItems': 0,
    'evaluationCounts': dict(Counter(row['status'] for row in evaluation['cases'])),
    'exactDuplicateRecords': duplicates}
write_json(ROOT / 'reports/sol-checks.json', result)
print(result)

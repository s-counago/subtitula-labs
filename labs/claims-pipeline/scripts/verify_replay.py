"""Verify cached inference and duplicate-safe import offline, without changing the original run's manifest."""
import json
import requests
from common import ROOT, read_json, sha, write_json, now
from pipeline import Runner

config = read_json(ROOT / 'config/experiment.json')
frozen = read_json(ROOT / 'reference/frozen.json')
runner = Runner(config, frozen)
source_path = runner.path
before = {str(p.relative_to(source_path)): sha(p) for p in source_path.glob('receipts/*.json')}
requests.post = lambda *a, **k: (_ for _ in ()).throw(AssertionError('Network POST attempted during offline replay'))
stages = []
for request_path in sorted((source_path / 'requests').glob('*.json')):
    request = read_json(request_path)
    stage = request_path.stem
    runner.infer(stage, request['messages'][0]['content'], json.loads(request['messages'][1]['content']), request['response_format']['json_schema']['schema'])
    stages.append(stage)
after = {str(p.relative_to(source_path)): sha(p) for p in source_path.glob('receipts/*.json')}
assert before == after

runner.catalog = read_json(source_path / 'matters.json')
runner.mentions = read_json(source_path / 'mentions.json')
runner.claims = read_json(source_path / 'claims.json')
runner.rejections = read_json(source_path / 'rejections.json')
runner.blocks = read_json(source_path / 'blocks.json')
runner.path = ROOT / 'reports/replay-check'
first = runner.persist()['counts']
second = runner.persist()['counts']
assert first == second == read_json(source_path / 'summary.json')['counts']
write_json(ROOT / 'reports/replay-proof.json', {'checkedAt': now(), 'cachedStages': stages,
    'networkPostsAllowed': False, 'networkPostsAttempted': 0, 'originalReceiptsUnchanged': True,
    'countsAfterFirstImport': first, 'countsAfterSecondImport': second,
    'semanticDuplicateDetection': False,
    'note': 'Unique operation IDs prevent duplicate imports; repeated model claims within one response remain a separate quality problem.'})
print({'cachedStages': len(stages), 'networkPosts': 0, 'duplicateImportCountsUnchanged': first})

"""Compare completed Luna runs using preserved provider counters, not text estimates."""
from collections import Counter
from datetime import datetime
from common import ROOT, read_json, write_json, now

RUNS = {
    'low': ('vigo-2025-12-23-luna-v1', 'evaluation-luna.json'),
    'xhigh': ('vigo-2025-12-23-luna-xhigh-v1b', 'evaluation-luna-xhigh.json'),
}

def summarize(run_id, evaluation_file):
    path = ROOT / 'runs' / run_id
    manifest = read_json(path / 'manifest.json')
    if manifest['state'] not in {'completed', 'completed_with_errors'}:
        raise RuntimeError('The requested run has not finished.')
    receipts = [read_json(p) for p in sorted((path / 'receipts').glob('*.json'))]
    if any(r['state'] != 'completed' for r in receipts):
        raise RuntimeError('A model operation has no completed usage receipt.')
    keys = ['input_tokens', 'cached_input_tokens', 'cache_write_input_tokens',
            'output_tokens', 'reasoning_output_tokens']
    usage = {key: sum(r['reportedCodexUsage'].get(key, 0) for r in receipts) for key in keys}
    assert all(r['reportedCodexUsage']['input_tokens'] < 272000 for r in receipts)
    assert usage['reasoning_output_tokens'] <= usage['output_tokens']
    usage['total_input_and_output_tokens'] = usage['input_tokens'] + usage['output_tokens']
    usage['non_reasoning_output_tokens'] = usage['output_tokens'] - usage['reasoning_output_tokens']
    estimated = ((usage['input_tokens'] - usage['cached_input_tokens'] - usage['cache_write_input_tokens']) * .20
                 + usage['cached_input_tokens'] * .02 + usage['cache_write_input_tokens'] * .25
                 + usage['output_tokens'] * 1.20) / 1_000_000
    claims = read_json(path / 'claims.json')
    duplicate_count = len(claims) - len({(c['statement'], c['speakerId'], tuple(c['evidenceSegmentIds'])) for c in claims})
    counts = Counter(row['status'] for row in read_json(ROOT / 'reports' / evaluation_file)['cases'])
    elapsed = (datetime.fromisoformat(manifest['finishedAt']) - datetime.fromisoformat(manifest['startedAt'])).total_seconds()
    return {'experimentId': run_id, 'state': manifest['state'], 'model': manifest['model'],
        'reasoningEffort': manifest['reasoningEffort'], 'operations': len(receipts),
        'usage': usage, 'elapsedSeconds': round(elapsed, 3),
        'estimatedApiEquivalentUsd': round(estimated, 9), 'apiEquivalentIsCharge': False,
        'quality': {key: counts.get(key, 0) for key in ['faithful', 'partial', 'invalid', 'missed']},
        'savedCandidates': len(claims), 'rejectedCandidates': len(read_json(path / 'rejections.json')),
        'exactDuplicateRecords': duplicate_count,
        'operationsDetail': [{'stage': r['stage'], 'elapsedSeconds': r['elapsedSeconds'],
            'usage': r['reportedCodexUsage']} for r in receipts]}

results = {effort: summarize(*values) for effort, values in RUNS.items()}
low, high = results['low'], results['xhigh']
ratios = {
    'totalTokensRatio': high['usage']['total_input_and_output_tokens'] / low['usage']['total_input_and_output_tokens'],
    'reasoningTokensRatio': high['usage']['reasoning_output_tokens'] / low['usage']['reasoning_output_tokens'],
    'elapsedTimeRatio': high['elapsedSeconds'] / low['elapsedSeconds'],
    'apiEquivalentRatio': high['estimatedApiEquivalentUsd'] / low['estimatedApiEquivalentUsd'],
    'additionalFaithfulCases': high['quality']['faithful'] - low['quality']['faithful'],
}
interrupted_path = ROOT / 'runs/vigo-2025-12-23-luna-xhigh-v1'
interrupted = read_json(interrupted_path / 'manifest.json')
assert interrupted['state'] == 'interrupted'
document = {'createdAt': now(), 'runs': results, 'comparison': ratios,
    'interruptedAttempt': {'experimentId': interrupted['experimentId'], 'localTimeLimitSeconds': 360,
        'usage': None, 'apiEquivalentUsd': None, 'includedInCompletedRunTotals': False},
    'auxiliaryProbes': {
        'low': read_json(ROOT / 'runs/luna-transport-preflight/receipt.json'),
        'xhigh': read_json(ROOT / 'runs/luna-xhigh-transport-probe/receipt.json')},
    'scope': 'Completed extraction and matter-resolution operations; excludes evaluator work, both transport probes and the interrupted attempt.',
    'reasoningCounterIsSubsetOfOutput': True,
    'actualBilling': 'chatgpt_subscription_limits',
    'apiPriceSource': 'https://developers.openai.com/api/docs/models/gpt-5.6-luna',
    'reasoningAccountingSource': 'https://developers.openai.com/api/docs/guides/reasoning',
    'limitations': ['The total consumption of all xhigh attempts is unknown because the interrupted attempt had no usage receipt.',
        'API equivalents use Codex counters and published API rates; they are not invoices.',
        'One completed run per effort does not measure stochastic variance.']}
write_json(ROOT / 'reports/luna-effort-metrics.json', document)
print({'comparison': ratios, 'runs': {k: {'usage': v['usage'], 'quality': v['quality'],
    'seconds': v['elapsedSeconds'], 'apiEquivalentUsd': v['estimatedApiEquivalentUsd']} for k,v in results.items()}})

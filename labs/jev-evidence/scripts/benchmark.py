import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import experiment as base

ROOT = base.ROOT
SUITE = ROOT / 'fixtures/v2'
LABELS = ['supported', 'contradicted', 'insufficient', 'conflicting', 'not_verifiable']


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_suite():
    base.verify_inputs()
    manifest = base.read(SUITE / 'manifest.json')
    for prefix, hashes in [(SUITE, manifest['files']), (ROOT, manifest['parents'])]:
        for name, expected in hashes.items():
            if file_hash(prefix / name) != expected:
                raise ValueError(f'Frozen dependency changed: {name}')
    reference = base.read(SUITE / 'reference.json')
    policy = base.read(SUITE / 'policy.json')
    fixtures = {c['fixtureId']: base.read(SUITE / 'requests' / f"{c['fixtureId']}.json") for c in reference['cases']}
    for key, request in fixtures.items():
        if len(base.encoded(request)) > policy['maxRequestBytes'] or request['model'] != policy['model']:
            raise ValueError(f'Invalid request: {key}')
    return fixtures, reference, policy


def preflight_reason(request):
    evidence = request['state']['externalEvidence']
    if not evidence:
        return 'missing_evidence'
    if all(s['kind'] == 'reported_statement' for s in evidence):
        return 'only_reported_statements'
    return None


def guarded_decision(request, response, policy):
    reason = preflight_reason(request)
    if reason:
        return dict(action='abstain', reason=reason, candidate=None)
    if response is None:
        return dict(action='abstain', reason='technical_failure', candidate=None)
    answer = response['answers']['assessment']
    choice = answer['choice']
    if choice not in ('supported', 'contradicted'):
        return dict(action='abstain', reason=choice, candidate=None)
    if answer['confidence'] < policy['confidenceThreshold']:
        return dict(action='abstain', reason='low_confidence', candidate=None)
    relations = [a['choice'] for key, a in response['answers'].items() if key != 'assessment']
    required = 'supports' if choice == 'supported' else 'contradicts'
    opposite = 'contradicts' if choice == 'supported' else 'supports'
    if required not in relations or opposite in relations:
        return dict(action='abstain', reason='source_relations_do_not_agree', candidate=None)
    return dict(action='experimental_candidate', reason='passes_provisional_gates', candidate=choice)


def sequence(fixtures, policy, selection, repeats):
    ids = list(fixtures) if selection == 'full' else policy[f'{selection}Ids']
    jobs = [(f'{key}-r{repeat}', key) for repeat in range(1, repeats + 1) for key in ids]
    if repeats < 1 or repeats > 3 or len(jobs) > policy['maxCalls']:
        raise ValueError('Maximum 3 repeats and 72 calls per run')
    return jobs


def plan(fixtures, reference, policy, jobs, mode):
    active = [(key, fixtures[fixture]) for key, fixture in jobs
              if mode == 'diagnostic' or preflight_reason(fixtures[fixture]) is None]
    chars = sum(len(base.encoded(r).decode('utf-8')) for _, r in active)
    questions = sum(len(r['questions']) for _, r in active)
    low = math.ceil(chars / 4) + 32 * questions
    high = math.ceil(chars / 2) + 256 * questions
    return dict(createdAt=base.now(), providerCalls=0, selectedItems=len(jobs), plannedHttpCalls=len(active),
        locallyAbstainedItems=len(jobs)-len(active), mode=mode,
        requestBytes=sum(len(base.encoded(r)) for _, r in active), questions=questions,
        inputTokenScenario=[low, high],
        directCostScenarioUSD=[round(n * policy['directInputPricePerMillion'] / 1_000_000, 8) for n in (low, high)],
        estimateMethod='Illustrative scenarios: JSON characters / 4 + 32 per question; JSON characters / 2 + 256 per question. Not the Jev tokenizer, not bounds or measured usage.',
        priceSource=policy['priceSource'], priceCheckedOn=policy['priceCheckedOn'],
        excludes=['source search', 'PDF extraction', 'manual preparation', 'taxes', 'gateway fees', 'provider serialization differences'],
        latencyMeasured=False, accuracyMeasured=False, referenceHumanReviewed=False)


def valid_usage(raw):
    usage = raw.get('usage', {}) if isinstance(raw, dict) else {}
    if all(type(usage.get(k)) is int and usage[k] >= 0 for k in ('input_tokens', 'output_tokens')):
        return usage
    return None


def evaluate_once(endpoint, token, request, directory, job_id, timeout):
    receipt_path = directory / f'{job_id}.receipt.json'
    if receipt_path.exists():
        receipt = base.read(receipt_path)
        if receipt['requestSha256'] != base.digest(request):
            raise ValueError('Cached request changed')
        if receipt['status'] not in ('completed', 'local_abstention'):
            raise ValueError('Prior failed or uncertain attempt: no automatic resend')
        if receipt['status'] == 'completed':
            raw_path = directory / f'{job_id}.response.json'
            if file_hash(raw_path) != receipt['rawSha256']:
                raise ValueError('Cached response changed')
            base.validate_response(base.read(raw_path), request)
        return receipt
    base.write(directory / f'{job_id}.request.json', request)
    receipt = dict(startedAt=base.now(), status='in_flight', requestSha256=base.digest(request),
                   provider='typesafe', attempted=True)
    base.write(receipt_path, receipt)
    started = time.perf_counter()
    try:
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        with urlopen(Request(endpoint, data=base.encoded(request), headers=headers, method='POST'), timeout=timeout) as result:
            raw_bytes = result.read()
            receipt['httpStatus'] = result.status
        raw_path = directory / f'{job_id}.response.json'
        raw_path.write_bytes(raw_bytes)
        receipt['rawSha256'] = file_hash(raw_path)
        raw = json.loads(raw_bytes)
        receipt['usage'] = valid_usage(raw)
        base.validate_response(raw, request)
        receipt['status'] = 'completed'
    except HTTPError as error:
        receipt.update(status='http_error', httpStatus=error.code, errorType='HTTPError')
    except (URLError, TimeoutError, ValueError, KeyError, TypeError, AttributeError, OSError) as error:
        receipt.update(status='failed_or_uncertain', errorType=type(error).__name__)
    finally:
        receipt.update(finishedAt=base.now(), seconds=round(time.perf_counter()-started, 6))
        base.write(receipt_path, receipt)
    return receipt


def metric_group(rows):
    completed = [r for r in rows if r['status'] == 'completed']
    eligible = [r for r in completed if r['scored']]
    confusion = {label: {p: 0 for p in LABELS} for label in LABELS}
    for row in eligible:
        confusion[row['expected']][row['choice']] += 1
    candidates = [r for r in eligible if r['guard']['action'] == 'experimental_candidate']
    count = len(eligible)
    return dict(completed=len(completed), scored=count, correct=sum(r['correct'] for r in eligible),
        agreementRate=sum(r['correct'] for r in eligible)/count if count else None,
        falseSupport=sum(r['choice'] == 'supported' and r['expected'] != 'supported' for r in eligible),
        falseContradiction=sum(r['choice'] == 'contradicted' and r['expected'] != 'contradicted' for r in eligible),
        predictedSupport=sum(r['choice'] == 'supported' for r in eligible),
        predictedContradiction=sum(r['choice'] == 'contradicted' for r in eligible),
        confusion=confusion, candidateCount=len(candidates),
        candidateErrors=sum(not r['correct'] for r in candidates),
        candidateCoverage=len(candidates)/count if count else None,
        candidatePrecision=sum(r['correct'] for r in candidates)/len(candidates) if candidates else None)


def summarize(directory, fixtures, reference, policy, jobs):
    by_id = {r['fixtureId']: r for r in reference['cases']}
    rows = []
    known_input = known_output = 0
    unknown = []
    durations = []
    for job, key in jobs:
        ref = by_id[key]
        request = fixtures[key]
        path = directory / f'{job}.receipt.json'
        receipt = base.read(path) if path.exists() else dict(status='not_attempted', attempted=False)
        if path.exists() and receipt['requestSha256'] != base.digest(request):
            raise ValueError('Receipt does not match the frozen request')
        row = dict(jobId=job, fixtureId=key, origin=ref['origin'], challenge=ref['challenge'],
                   expected=ref['expected'], scored=ref['scored'], status=receipt['status'],
                   attempted=receipt.get('attempted', False))
        raw = None
        if receipt['status'] == 'completed':
            raw_path = directory / f'{job}.response.json'
            if file_hash(raw_path) != receipt['rawSha256']:
                raise ValueError('Response hash mismatch')
            raw = base.validate_response(base.read(raw_path), request)
            answer = raw['answers']['assessment']
            row.update(choice=answer['choice'], confidence=answer['confidence'], probabilities=answer['probabilities'],
                       correct=answer['choice'] == ref['expected'], seconds=receipt['seconds'])
            durations.append(receipt['seconds'])
        if receipt.get('usage'):
            known_input += receipt['usage']['input_tokens']
            known_output += receipt['usage']['output_tokens']
        elif receipt.get('attempted'):
            unknown.append(job)
        row['guard'] = guarded_decision(request, raw, policy)
        rows.append(row)
    complete = [r for r in rows if r['status'] == 'completed']
    consistency = []
    for group in policy['semanticInvariantGroups']:
        members = [r for r in complete if r['fixtureId'] in group]
        choices = sorted(set(r['choice'] for r in members))
        consistency.append(dict(fixtures=group, observed=len(members), labels=choices,
                                consistent=len(choices) == 1 if len(members) >= 2 else None))
    repeatability = []
    for key in fixtures:
        members = [r for r in complete if r['fixtureId'] == key]
        if len(members) > 1:
            repeatability.append(dict(fixtureId=key, repeats=len(members),
                sameLabel=len({r['choice'] for r in members}) == 1,
                confidenceRange=max(r['confidence'] for r in members)-min(r['confidence'] for r in members)))
    summary = dict(createdAt=base.now(), suite='jev-fixtures-v2', selected=len(jobs), completed=len(complete),
        attempted=sum(r['attempted'] for r in rows), localAbstentions=sum(r['status'] == 'local_abstention' for r in rows),
        notAttempted=sum(r['status'] == 'not_attempted' for r in rows),
        real=metric_group([r for r in rows if r['origin'] == 'real_extraction']),
        controls=metric_group([r for r in rows if r['origin'] == 'controlled_variant']),
        knownInputTokens=known_input, knownOutputTokens=known_output, unknownConsumption=unknown,
        knownDirectCostEquivalentUSD=round(known_input * policy['directInputPricePerMillion']/1_000_000, 8),
        latency=dict(successfulSample=len(durations), p50Seconds=statistics.median(durations) if durations else None,
                     p95Seconds=sorted(durations)[math.ceil(.95*len(durations))-1] if durations else None,
                     method='p50 median; p95 nearest-rank; successful HTTP calls only; descriptive for this small correlated sample'),
        consistency=consistency, repeatability=repeatability, results=rows,
        caveats=['assistant reference, no independent human review', 'R03 exploratory, excluded from scored metrics',
                 'correlated cases from one session, not a production accuracy estimate', 'threshold 0.85 provisional, not calibrated',
                 'no automatic publication', 'known cost may be partial when a request fails', 'retrieval and preparation excluded'])
    base.write(directory / 'summary.json', summary)
    lines = ['# Benchmark de fixtures Jev', '',
        f"Completados {summary['completed']}/{summary['selected']}; intentos HTTP {summary['attempted']}; abstenciones locales {summary['localAbstentions']}.",
        '', '| Grupo | Casos puntuados | Coincidencias | Falsos apoyos | Falsas refutaciones |', '|---|---:|---:|---:|---:|']
    for key in ('real', 'controls'):
        group = summary[key]
        lines.append(f"| {key} | {group['scored']} | {group['correct']} | {group['falseSupport']} | {group['falseContradiction']} |")
    lines += ['', '| Caso | Estado | Referencia | Jev | Decisión con controles |', '|---|---|---|---|---|']
    for r in rows:
        lines.append(f"| {r['jobId']} | {r['status']} | {r['expected']} | {r.get('choice', '—')} | {r['guard']['reason']} |")
    lines += ['', f"Tokens conocidos: {known_input} entrada + {known_output} salida. Equivalencia directa: USD {summary['knownDirectCostEquivalentUSD']:.8f}.",
              f"Intentos con consumo desconocido: {len(unknown)}. Latencia: {json.dumps(summary['latency'], ensure_ascii=False)}.", '',
              'R03 se informa como exploratorio. Los controles no son afirmaciones reales adicionales. Los casos repetidos no son observaciones independientes.',
              'La confianza y el umbral 0,85 no están calibrados para plenos; pasar los controles solo produce una propuesta experimental.']
    (directory / 'results.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'run', 'replay'])
    parser.add_argument('--selection', choices=['smoke', 'full', 'repeatability'], default='smoke')
    parser.add_argument('--mode', choices=['diagnostic', 'guarded'], default='diagnostic')
    parser.add_argument('--repeats', type=int, default=1)
    parser.add_argument('--run-id', default='fixtures-v2-smoke')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,60}', args.run_id):
        raise ValueError('Invalid run ID')
    fixtures, reference, policy = load_suite()
    jobs = sequence(fixtures, policy, args.selection, args.repeats)
    if args.action == 'prepare':
        estimates = {mode: plan(fixtures, reference, policy, jobs, mode) for mode in ('diagnostic', 'guarded')}
        base.write(ROOT / 'reports' / f'fixtures-v2-{args.selection}-plan.json', estimates)
        print(json.dumps(estimates, ensure_ascii=False, indent=2))
        return
    directory = ROOT / 'runs' / args.run_id
    manifest_path = directory / 'benchmark-manifest.json'
    if args.action == 'replay':
        manifest = base.read(manifest_path)
        if manifest['suiteSha256'] != file_hash(SUITE / 'manifest.json'):
            raise ValueError('Suite differs from recorded run')
        jobs = [tuple(j) for j in manifest['jobs']]
        summarize(directory, fixtures, reference, policy, jobs)
        print(f'Replayed {len(jobs)} scheduled items without network access.')
        return
    manifest = dict(suiteSha256=file_hash(SUITE / 'manifest.json'), runnerSha256=file_hash(Path(__file__)),
                    jobs=jobs, mode=args.mode, provider='typesafe', simulated=False)
    if manifest_path.exists() and base.encoded(base.read(manifest_path)) != base.encoded(manifest):
        raise ValueError('Run configuration changed; preserve this run and choose a new ID')
    endpoint, token = base.credentials('typesafe')
    directory.mkdir(parents=True, exist_ok=True)
    base.write(manifest_path, manifest)
    for job_id, key in jobs:
        request = fixtures[key]
        reason = preflight_reason(request) if args.mode == 'guarded' else None
        if reason:
            receipt_path = directory / f'{job_id}.receipt.json'
            receipt = dict(status='local_abstention', attempted=False, reason=reason, requestSha256=base.digest(request))
            if receipt_path.exists() and base.read(receipt_path) != receipt:
                raise ValueError('Local decision changed')
            base.write(receipt_path, receipt)
            base.write(directory / f'{job_id}.request.json', request)
        else:
            receipt = evaluate_once(endpoint, token, request, directory, job_id, policy['timeoutSeconds'])
        print(json.dumps(dict(jobId=job_id, status=receipt['status'])), flush=True)
        if receipt['status'] not in ('completed', 'local_abstention'):
            break
    summarize(directory, fixtures, reference, policy, jobs)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError) as error:
        raise SystemExit(str(error))

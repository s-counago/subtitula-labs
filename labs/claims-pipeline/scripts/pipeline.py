"""Bounded GLM experiment with saved requests, cited proposals and local transactional persistence."""
import argparse
import hashlib
import json
import re
import sqlite3
import time
import uuid
import requests
from common import ROOT, cloudflare_key, now, read_json, sha, write_json
from contracts import EXTRACTION_SCHEMA, RESOLUTION_SCHEMA, normalize_space, validate_shape, validate_claim, ValidationError

def stable_id(kind, operation):
    return kind + '-' + str(uuid.uuid5(uuid.NAMESPACE_URL, 'claims-lab:' + operation))

def build_blocks(segments, max_characters):
    blocks, current, count = [], [], 0
    for segment in segments:
        if current and count + len(segment['text']) > max_characters:
            blocks.append(current)
            current, count = [], 0
        current.append(segment)
        count += len(segment['text'])
    if current:
        blocks.append(current)
    return blocks

def public_segment(segment):
    return {k: segment[k] for k in ['id', 'start', 'end', 'speakerId', 'text']}

def recover_context(requests_to_read, segments, config):
    """Read only local corpus; query is literal case-insensitive text, not shell/SQL."""
    by_id = {s['id']: s for s in segments}
    retrieved, ledger, total = {}, [], 0
    for req in requests_to_read[:config['maxContextRequests']]:
        anchor = by_id.get(req['anchorSegmentId'])
        found = []
        if anchor:
            found += [s for s in segments if abs(s['sequence'] - anchor['sequence']) <= 5]
        if req['query']:
            query = normalize_space(req['query']).casefold()
            found += [s for s in segments if query in normalize_space(s['text']).casefold()][:5]
        returned = []
        for s in found:
            if s['id'] in retrieved:
                returned.append(s['id'])
                continue
            if total + len(s['text']) > config['maxContextCharacters']:
                continue
            retrieved[s['id']] = s
            returned.append(s['id'])
            total += len(s['text'])
        ledger.append({'request': req, 'returnedIds': list(dict.fromkeys(returned)),
                       'scope': 'same_transcript', 'characterBudget': config['maxContextCharacters']})
    return sorted(retrieved.values(), key=lambda s: s['sequence']), ledger

class Runner:
    def __init__(self, config, frozen):
        self.config = config
        self.path = ROOT / 'runs' / config['experimentId']
        self.path.mkdir(parents=True, exist_ok=True)
        self.token = None
        self.manifest_path = self.path / 'manifest.json'
        hashes = {p: sha(ROOT / p) for p in ['config/experiment.json', 'config/extraction-prompt.txt',
            'config/resolution-prompt.txt', 'scripts/pipeline.py', 'scripts/contracts.py', 'scripts/common.py']}
        if self.manifest_path.exists():
            existing = read_json(self.manifest_path)
            if existing['inputHashes'] != hashes or existing['referenceSha256'] != frozen['referenceSha256']:
                raise RuntimeError('Inputs changed. Preserve this run and choose a new experimentId.')
        else:
            write_json(self.manifest_path, {'startedAt': now(), 'experimentId': config['experimentId'],
                'model': config['model'], 'referenceSha256': frozen['referenceSha256'],
                'referenceFrozenAt': frozen['frozenAt'], 'segmentsSha256': frozen['segmentsSha256'],
                'inputHashes': hashes, 'referenceContentsProvidedToModel': False, 'state': 'running'})
        self.catalog = []
        self.mentions = []
        self.claims = []
        self.rejections = []
        self.blocks = []

    def infer(self, stage, prompt, payload, schema):
        request = {'messages': [{'role': 'system', 'content': prompt},
            {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)}],
            'temperature': self.config['temperature'], 'seed': self.config['seed'],
            'max_tokens': self.config['maxOutputTokens'], 'chat_template_kwargs': {'enable_thinking': False},
            'reasoning_effort': None, 'response_format': {'type': 'json_schema',
            'json_schema': {'name': 'lab_' + stage.replace('-', '_'), 'strict': True, 'schema': schema}}}
        req_path = self.path / 'requests' / (stage + '.json')
        raw_path = self.path / 'responses' / (stage + '.json')
        receipt_path = self.path / 'receipts' / (stage + '.json')
        if req_path.exists() and read_json(req_path) != request:
            raise RuntimeError('Saved request differs. Create a new run instead of overwriting it.')
        if raw_path.exists():
            if receipt_path.exists() and read_json(receipt_path)['state'] != 'completed':
                raise RuntimeError('Saved model request did not complete successfully; inspect before recovery.')
            raw = read_json(raw_path)
        else:
            if receipt_path.exists():
                raise RuntimeError('Unfinished or failed paid operation exists; inspect it before explicit recovery.')
            if len(list((self.path / 'receipts').glob('*.json'))) >= self.config['maxModelRequests']:
                raise RuntimeError('Experiment model-request budget reached.')
            write_json(req_path, request)
            receipt = {'stage': stage, 'startedAt': now(), 'requestSha256': sha(req_path), 'state': 'sending'}
            write_json(receipt_path, receipt)
            if self.token is None:
                self.token = cloudflare_key()
            started = time.monotonic()
            try:
                response = requests.post(
                    f"https://api.cloudflare.com/client/v4/accounts/{self.config['cloudflareAccountId']}/ai/run/{self.config['model']}",
                    headers={'Authorization': 'Bearer ' + self.token}, json=request, timeout=(30, 240))
                raw = response.json()
                write_json(raw_path, raw)
                result = raw.get('result') or raw
                receipt.update({'finishedAt': now(), 'elapsedSeconds': round(time.monotonic() - started, 3),
                    'httpStatus': response.status_code, 'state': 'completed' if response.ok and raw.get('success', True) else 'failed',
                    'responseSha256': sha(raw_path), 'usage': result.get('usage'),
                    'finishReason': (result.get('choices') or [{}])[0].get('finish_reason'),
                    'errorCodes': [e.get('code') for e in raw.get('errors', [])]})
                write_json(receipt_path, receipt)
                print({'stage': stage, 'http': response.status_code, 'seconds': receipt['elapsedSeconds'],
                       'usage': receipt['usage'], 'finish': receipt['finishReason']}, flush=True)
                if receipt['state'] != 'completed':
                    raise RuntimeError('Model request failed. Inspect receipt; no automatic retry.')
            except requests.RequestException as error:
                receipt.update({'state': 'uncertain', 'finishedAt': now(), 'errorType': type(error).__name__})
                write_json(receipt_path, receipt)
                raise RuntimeError('Network outcome uncertain; no automatic paid retry.') from None
        result = raw.get('result') or raw
        choices = result.get('choices', [])
        if choices:
            if choices[0].get('finish_reason') == 'length':
                raise ValueError('truncated_model_output')
            content = choices[0]['message'].get('content')
        else:
            content = result.get('response')
        parsed = json.loads(content) if isinstance(content, str) else content
        validate_shape(parsed, schema)
        write_json(self.path / 'parsed' / (stage + '.json'), parsed)
        return parsed

    def resolve(self, stage, matters, accepted, by_id, allowed_ids):
        used_keys = {c['matterKey'] for c in accepted}
        mentions = []
        for m in matters:
            if m['key'] not in used_keys:
                continue
            mid = stable_id('mention', self.config['experimentId'] + ':' + stage + ':' + m['key'])
            mention = {**m, 'mentionId': mid, 'canonicalId': None, 'resolutionState': 'pending'}
            ids = m['evidenceSegmentIds']
            if not ids or set(ids) - set(allowed_ids) or set(ids) - set(by_id):
                mention['resolutionReason'] = 'Invalid or unavailable matter evidence'
                self.mentions.append(mention)
                continue
            mention['sourceText'] = ' '.join(by_id[k]['text'] for k in ids)
            mentions.append(mention)
        if mentions:
            payload = {'session': {k: self.config[k] for k in ['institution', 'territory', 'sessionDate', 'agenda']},
                       'mentions': mentions, 'catalog': self.catalog}
            prompt = (ROOT / 'config/resolution-prompt.txt').read_text(encoding='utf-8')
            decision = self.infer(stage + '-matters', prompt, payload, RESOLUTION_SCHEMA)
            ids = [d['mentionId'] for d in decision['decisions']]
            if len(ids) != len(set(ids)) or set(ids) != {m['mentionId'] for m in mentions}:
                raise ValueError('resolver_missing_duplicate_or_unknown_mention')
            decisions = {d['mentionId']: d for d in decision['decisions']}
            resolved = {}
            for mention in mentions:
                d = decisions[mention['mentionId']]
                cid = None
                reason = d['reason']
                if d['action'] == 'new' and d['canonicalId'] is None and d['canonicalLabel']:
                    cid = stable_id('matter', mention['mentionId'])
                    self.catalog.append({'id': cid, 'label': d['canonicalLabel'], 'object': mention['object'],
                        'territory': mention['territory'], 'institution': mention['institution'],
                        'referencePeriod': mention['referencePeriod'], 'originMentionId': mention['mentionId'],
                        'reviewState': 'proposed'})
                elif d['action'] == 'existing':
                    candidate = resolved.get(d['canonicalId'], d['canonicalId'])
                    if candidate and candidate in {c['id'] for c in self.catalog}:
                        cid = candidate
                    else:
                        reason = 'Rejected unknown or forward canonical reference: ' + reason
                elif d['action'] != 'pending' or d['canonicalId'] is not None:
                    reason = 'Rejected inconsistent resolution fields: ' + reason
                mention.update({'canonicalId': cid, 'resolutionState': 'proposed' if cid else 'pending',
                                'resolutionReason': reason, 'modelAction': d['action']})
                resolved[mention['mentionId']] = cid
                self.mentions.append(mention)
        return {m['key']: m for m in self.mentions if m['mentionId'] == stable_id('mention', self.config['experimentId'] + ':' + stage + ':' + m['key'])}

    def persist(self):
        write_json(self.path / 'claims.json', self.claims)
        write_json(self.path / 'matters.json', self.catalog)
        write_json(self.path / 'mentions.json', self.mentions)
        write_json(self.path / 'rejections.json', self.rejections)
        write_json(self.path / 'blocks.json', self.blocks)
        database = sqlite3.connect(self.path / 'proposals.sqlite')
        database.execute('PRAGMA foreign_keys=ON')
        database.executescript('''
            CREATE TABLE IF NOT EXISTS matters(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS mentions(id TEXT PRIMARY KEY, matter_id TEXT REFERENCES matters(id), payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS claims(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS occurrences(id TEXT PRIMARY KEY, claim_id TEXT NOT NULL REFERENCES claims(id),
                mention_id TEXT REFERENCES mentions(id), operation_id TEXT NOT NULL UNIQUE, payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS citations(occurrence_id TEXT NOT NULL REFERENCES occurrences(id),
                segment_id TEXT NOT NULL, role TEXT NOT NULL, PRIMARY KEY(occurrence_id,segment_id,role));
        ''')
        with database:
            for matter in self.catalog:
                database.execute('INSERT OR IGNORE INTO matters VALUES (?,?)', (matter['id'], json.dumps(matter, ensure_ascii=False)))
            for mention in self.mentions:
                database.execute('INSERT OR IGNORE INTO mentions VALUES (?,?,?)', (mention['mentionId'], mention['canonicalId'], json.dumps(mention, ensure_ascii=False)))
            for claim in self.claims:
                database.execute('INSERT OR IGNORE INTO claims VALUES (?,?)', (claim['claimId'], json.dumps(claim, ensure_ascii=False)))
                database.execute('INSERT OR IGNORE INTO occurrences VALUES (?,?,?,?,?)',
                    (claim['occurrenceId'], claim['claimId'], claim['mentionId'], claim['operationId'], json.dumps(claim, ensure_ascii=False)))
                for role, key in [('evidence', 'evidenceSegmentIds'), ('context', 'contextSegmentIds')]:
                    for segment_id in claim[key]:
                        database.execute('INSERT OR IGNORE INTO citations VALUES (?,?,?)', (claim['occurrenceId'], segment_id, role))
        counts = {table: database.execute('SELECT COUNT(*) FROM ' + table).fetchone()[0]
                  for table in ['matters', 'mentions', 'claims', 'occurrences', 'citations']}
        database.close()
        receipts = [read_json(p) for p in (self.path / 'receipts').glob('*.json')]
        usage = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
        missing = []
        for r in receipts:
            if not r.get('usage'):
                missing.append(r['stage'])
                continue
            for key in usage:
                usage[key] += r['usage'].get(key, 0)
        cost = (usage['prompt_tokens'] * self.config['pricePerMillionInputTokens'] +
                usage['completion_tokens'] * self.config['pricePerMillionOutputTokens']) / 1_000_000
        summary = {'updatedAt': now(), 'counts': counts, 'rejectedCandidates': len(self.rejections),
                   'requests': len(receipts), 'reportedUsage': usage, 'usageMissingFor': missing,
                   'estimatedGenerationCostUsdFromReportedTokens': cost,
                   'costIsInvoice': False, 'contextRounds': len(list((self.path / 'context').glob('*.json')))}
        write_json(self.path / 'summary.json', summary)
        return summary

def main():
    config = read_json(ROOT / 'config/experiment.json')
    frozen = read_json(ROOT / 'reference/frozen.json')
    for path, field in [('reference/gold.json', 'referenceSha256'),
                        ('inputs/transcripts/scribe-v2.json', 'transcriptSha256'),
                        ('inputs/transcripts/segments.json', 'segmentsSha256')]:
        if sha(ROOT / path) != frozen[field]:
            raise RuntimeError('Frozen reference or transcript changed.')
    runner = Runner(config, frozen)
    segments = read_json(ROOT / 'inputs/transcripts/segments.json')['segments']
    by_id = {s['id']: s for s in segments}
    blocks = build_blocks(segments, config['maxBlockCharacters'])
    prompt = (ROOT / 'config/extraction-prompt.txt').read_text(encoding='utf-8')
    for index, core in enumerate(blocks, 1):
        stage = f'block-{index:02d}'
        start = max(0, core[0]['sequence'] - 1 - config['neighborSegments'])
        end = min(len(segments), core[-1]['sequence'] + config['neighborSegments'])
        available = segments[start:end]
        core_ids = [s['id'] for s in core]
        allowed_ids = {s['id'] for s in available}
        payload = {'session': {k: config[k] for k in ['sessionId', 'institution', 'territory', 'sessionDate', 'agenda']},
                   'coreSegmentIds': core_ids, 'segments': [public_segment(s) for s in available]}
        try:
            data = runner.infer(stage + '-extract', prompt, payload, EXTRACTION_SCHEMA)
            if data['contextRequests'] and config['maxContextRounds'] > 0:
                extra, ledger = recover_context(data['contextRequests'], segments, config)
                write_json(runner.path / 'context' / (stage + '.json'), {'ledger': ledger, 'segments': extra})
                payload['additionalContext'] = [public_segment(s) for s in extra]
                payload['previousContextRequests'] = data['contextRequests']
                allowed_ids.update(s['id'] for s in extra)
                data = runner.infer(stage + '-context', prompt, payload, EXTRACTION_SCHEMA)
            keys = [m['key'] for m in data['matters']]
            if len(keys) != len(set(keys)):
                raise ValueError('duplicate_matter_keys')
            accepted = []
            for candidate_index, candidate in enumerate(data['claims'], 1):
                reasons = validate_claim(candidate, by_id, allowed_ids, core_ids, set(keys))
                if reasons:
                    runner.rejections.append({'block': stage, 'candidateIndex': candidate_index,
                                              'reasons': reasons, 'candidate': candidate})
                else:
                    accepted.append({**candidate, 'candidateIndex': candidate_index})
            matters = runner.resolve(stage, data['matters'], accepted, by_id, allowed_ids)
            for candidate in accepted:
                operation = config['experimentId'] + ':' + stage + ':' + str(candidate['candidateIndex'])
                mention = matters.get(candidate['matterKey'])
                if mention is None:
                    runner.rejections.append({'block': stage, 'candidate': candidate, 'reasons': ['matter_not_registered']})
                    continue
                runner.claims.append({**candidate, 'operationId': operation,
                    'claimId': stable_id('claim', operation), 'occurrenceId': stable_id('appearance', operation),
                    'mentionId': mention['mentionId'], 'canonicalMatterId': mention['canonicalId'],
                    'sessionId': config['sessionId'], 'transcriptSha256': frozen['transcriptSha256'],
                    'start': by_id[candidate['evidenceSegmentIds'][0]]['start'],
                    'end': by_id[candidate['evidenceSegmentIds'][-1]]['end'], 'reviewState': 'proposed',
                    'identityResolution': 'one_claim_per_occurrence_in_v1', 'block': stage})
            runner.blocks.append({'id': stage, 'coreSegmentIds': core_ids, 'state': 'completed',
                'generatedCandidates': len(data['claims']), 'validatedCandidates': len(accepted),
                'notes': data['notes'], 'unresolvedContextRequests': data['contextRequests']})
        except (ValueError, ValidationError) as error:
            runner.blocks.append({'id': stage, 'coreSegmentIds': core_ids, 'state': 'invalid_output', 'error': str(error)[:300]})
        runner.persist()
    summary = runner.persist()
    manifest = read_json(runner.manifest_path)
    manifest.update({'finishedAt': now(), 'state': 'completed' if all(b['state'] == 'completed' for b in runner.blocks) else 'completed_with_errors'})
    write_json(runner.manifest_path, manifest)
    print(summary)

if __name__ == '__main__':
    main()

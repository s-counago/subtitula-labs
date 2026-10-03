"""Offline adversarial checks. No model or application calls."""
import copy
from common import ROOT, read_json
from contracts import validate_claim
from pipeline import recover_context, build_blocks

segments = read_json(ROOT / 'inputs/transcripts/segments.json')['segments']
by_id = {s['id']: s for s in segments}
base = {'evidenceSegmentIds': ['S0005'], 'contextSegmentIds': [], 'quote': by_id['S0005']['text'],
        'speakerId': by_id['S0005']['speakerId'], 'matterKey': 'M1', 'contextStatus': 'sufficient',
        'statement': 'Proposición de prueba', 'property': 'test'}
assert validate_claim(base, by_id, {'S0005'}, {'S0005'}, {'M1'}) == []
for change, expected in [({'quote': 'Esta cita fue inventada.'}, 'quote_not_literal'),
                         ({'speakerId': 'speaker_wrong'}, 'speaker_does_not_match_evidence'),
                         ({'evidenceSegmentIds': ['S9999']}, 'unknown_source'),
                         ({'contextSegmentIds': ['S0006']}, 'source_not_provided_to_model'),
                         ({'contextStatus': 'insufficient'}, 'insufficient_context')]:
    candidate = {**base, **change}
    assert expected in validate_claim(candidate, by_id, {'S0005'}, {'S0005'}, {'M1'}), expected
assert 'claim_belongs_to_context_not_current_block' in validate_claim(base, by_id, {'S0005'}, {'S0006'}, {'M1'})
config = read_json(ROOT / 'config/experiment.json')
parts = build_blocks(segments, config['maxBlockCharacters'])
assert [s['id'] for block in parts for s in block] == [s['id'] for s in segments]
extra, ledger = recover_context([{'anchorSegmentId': 'S0030', 'query': 'orzamento', 'reason': 'test'}] * 10, segments, config)
assert len(ledger) <= config['maxContextRequests']
assert sum(len(s['text']) for s in extra) <= config['maxContextCharacters']
assert all(s['id'] in by_id for s in extra)
print({'offlineChecks': 'passed', 'coreBlocks': len(parts), 'coreSegmentCounts': [len(p) for p in parts]})

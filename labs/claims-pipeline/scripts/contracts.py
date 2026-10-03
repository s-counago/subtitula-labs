"""Versioned strict output contracts and deterministic evidence checks."""
import sys
from common import ROOT
sys.path.insert(0, str(ROOT / '.vendor'))
import jsonschema
from jsonschema import ValidationError

def obj(properties):
    return {'type': 'object', 'properties': properties, 'required': list(properties), 'additionalProperties': False}

def arr(items, maximum=100):
    return {'type': 'array', 'items': items, 'maxItems': maximum}

TEXT = {'type': 'string'}
NULLTEXT = {'type': ['string', 'null']}
IDS = arr(TEXT, 8)
MATTER = obj({'key': TEXT, 'label': TEXT, 'object': TEXT, 'territory': NULLTEXT,
              'institution': NULLTEXT, 'referencePeriod': NULLTEXT, 'evidenceSegmentIds': IDS})
CLAIM = obj({'statement': TEXT, 'speakerId': TEXT, 'matterKey': TEXT, 'property': TEXT,
             'valueText': NULLTEXT, 'referencePeriod': NULLTEXT, 'conditions': arr(TEXT, 8),
             'modality': {'type': 'string', 'enum': ['asserted_fact', 'proposal', 'commitment', 'reported_statement', 'opinion']},
             'polarity': {'type': 'string', 'enum': ['positive', 'negative']},
             'evidenceSegmentIds': IDS, 'quote': TEXT, 'contextSegmentIds': IDS,
             'contextStatus': {'type': 'string', 'enum': ['sufficient', 'insufficient']}, 'uncertainty': NULLTEXT})
CONTEXT_REQUEST = obj({'anchorSegmentId': TEXT, 'query': NULLTEXT, 'reason': TEXT})
EXTRACTION_SCHEMA = obj({'matters': arr(MATTER, 15), 'claims': arr(CLAIM, 40),
                         'contextRequests': arr(CONTEXT_REQUEST, 3), 'notes': arr(TEXT, 10)})
RESOLUTION_SCHEMA = obj({'decisions': arr(obj({'mentionId': TEXT,
    'action': {'type': 'string', 'enum': ['existing', 'new', 'pending']},
    'canonicalId': NULLTEXT, 'canonicalLabel': NULLTEXT, 'reason': TEXT}), 15)})

def validate_shape(data, schema):
    jsonschema.Draft202012Validator(schema).validate(data)

def normalize_space(text):
    return ' '.join(text.split())

def validate_claim(claim, segment_map, allowed_ids, core_ids, matter_keys):
    reasons = []
    evidence = claim['evidenceSegmentIds']
    context = claim['contextSegmentIds']
    if not evidence:
        reasons.append('empty_evidence')
    if len(evidence) != len(set(evidence)) or len(context) != len(set(context)):
        reasons.append('duplicate_evidence_ids')
    if set(evidence + context) - set(allowed_ids):
        reasons.append('source_not_provided_to_model')
    if set(evidence + context) - set(segment_map):
        reasons.append('unknown_source')
        return reasons
    if evidence and evidence[0] not in core_ids:
        reasons.append('claim_belongs_to_context_not_current_block')
    if evidence != sorted(evidence, key=lambda key: segment_map[key]['sequence']):
        reasons.append('evidence_not_chronological')
    if any(segment_map[key]['speakerId'] != claim['speakerId'] for key in evidence):
        reasons.append('speaker_does_not_match_evidence')
    evidence_text = normalize_space(' '.join(segment_map[key]['text'] for key in evidence))
    if not normalize_space(claim['quote']) or normalize_space(claim['quote']) not in evidence_text:
        reasons.append('quote_not_literal')
    if claim['matterKey'] not in matter_keys:
        reasons.append('unknown_matter_key')
    if claim['contextStatus'] == 'insufficient':
        reasons.append('insufficient_context')
    if not claim['statement'].strip() or not claim['property'].strip():
        reasons.append('empty_statement_or_property')
    return reasons

"""Prepare reference-to-output candidates by shared sources, without auto-judging semantic matches."""
from common import ROOT, read_json, write_json
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--config', default='config/experiment.json')
parser.add_argument('--suffix', default='')
parser.add_argument('--id-prefix', default='C')
parser.add_argument('--quotes', action='store_true')
options = parser.parse_args()
assert all(c.isalnum() or c == '-' for c in options.suffix)
config = read_json(ROOT / options.config)
run = ROOT / 'runs' / config['experimentId']
claims = read_json(run / 'claims.json')
gold = read_json(ROOT / 'reference/gold.json')
packet = []
for expected in gold['cases']:
    candidates = []
    for index, actual in enumerate(claims, 1):
        if actual['speakerId'] == expected['speakerId'] and set(actual['evidenceSegmentIds']) & set(expected['evidenceSegmentIds']):
            candidates.append({'readingId': f'{options.id_prefix}{index:03d}', **actual})
    packet.append({'gold': expected, 'candidateMatchesBySourceOnly': candidates})
write_json(ROOT / ('reports/review-packet' + options.suffix + '.json'), packet)
for entry in packet:
    print(entry['gold']['id'], entry['gold']['expectedStatement'])
    for c in entry['candidateMatchesBySourceOnly']:
        print(' ', c['readingId'], c['statement'], '|', c['modality'], '| periodo:', c['referencePeriod'], '| condiciones:', c['conditions'])
        if options.quotes:
            print('  CITA:', c['quote'])

import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import experiment as lab


class ExperimentTests(unittest.TestCase):
    def setUp(self):
        self.cases = lab.read(lab.ROOT / 'inputs/cases.json')
        self.sources = lab.read(lab.ROOT / 'inputs/sources.json')
        self.protocol = lab.read(lab.ROOT / 'config/protocol.json')
        self.request = lab.build_request(self.cases[0], self.sources, self.protocol)

    def response(self):
        answers = {}
        for key, question in self.request['questions'].items():
            options = list(question['criteria'])
            answers[key] = dict(type='choice', choice=options[0], confidence=1,
                                probabilities={o: int(i == 0) for i, o in enumerate(options)})
        return dict(model=self.protocol['model'], answers=answers,
                    usage=dict(input_tokens=123, output_tokens=45))

    def test_frozen_evidence_and_original_extraction(self):
        lab.verify_inputs()
        provenance = lab.read(lab.ROOT / 'inputs/provenance.json')
        workspace = lab.ROOT.parent.parent
        for path_key, hash_key in [('extractionPath', 'extractionSha256'), ('transcriptPath', 'segmentsSha256')]:
            self.assertEqual(lab.hashlib.sha256((workspace / provenance[path_key]).read_bytes()).hexdigest(), provenance[hash_key])
        self.assertEqual(sum(c['kind'] == 'real_extraction' for c in self.cases), 4)

    def test_reference_never_reaches_provider(self):
        for case in self.cases:
            request = lab.build_request(case, self.sources, self.protocol)
            self.assertEqual(set(request), {'model', 'state', 'questions'})
            self.assertNotIn('expected', json.dumps(request))
            self.assertNotIn('rationale', json.dumps(request))
            self.assertNotIn('reference.json', json.dumps(request))
            self.assertLess(len(lab.encoded(request)), self.protocol['maxRequestBytes'])

    def test_absence_of_sources_stays_absent(self):
        case = next(c for c in self.cases if c['caseId'] == 'C03')
        request = lab.build_request(case, self.sources, self.protocol)
        self.assertEqual(request['state']['externalEvidence'], [])
        self.assertEqual(set(request['questions']), {'assessment'})

    def test_unknown_source_is_rejected(self):
        case = copy.deepcopy(self.cases[0])
        case['sourceIds'].append('invented')
        with self.assertRaises(ValueError):
            lab.build_request(case, self.sources, self.protocol)

    def test_vat_calculation_is_conditional_and_exact(self):
        case = next(c for c in self.cases if c['caseId'] == 'R04')
        state = lab.build_request(case, self.sources, self.protocol)['state']
        self.assertEqual(state['arithmetic']['grossEURPerTonne'], '104.50')
        self.assertIn('not an invoice', state['arithmetic']['condition'])
        reduced = copy.deepcopy(case)
        reduced['sourceIds'] = ['D05']
        self.assertNotIn('arithmetic', lab.build_request(reduced, self.sources, self.protocol)['state'])

    def test_invalid_model_outputs_are_rejected(self):
        mutations = [
            lambda r: r.update(model='some-other-model'),
            lambda r: r['answers'].pop('assessment'),
            lambda r: r['answers']['assessment'].update(choice='invented'),
            lambda r: r['answers']['assessment'].update(confidence=float('nan')),
            lambda r: r['answers']['assessment']['probabilities'].update(supported=-1),
            lambda r: r['answers']['assessment']['probabilities'].update(insufficient=1),
            lambda r: r['usage'].update(input_tokens=-1),
        ]
        for mutate in mutations:
            response = self.response()
            mutate(response)
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                lab.validate_response(response, self.request)

    def test_offline_replay_validates_receipts_and_tampering(self):
        with tempfile.TemporaryDirectory(prefix='jev-tests-') as directory:
            root = Path(directory)
            response = self.response()
            lab.write(root / 'R01.request.json', self.request)
            lab.write(root / 'R01.response.json', response)
            lab.write(root / 'R01.receipt.json', dict(status='completed', seconds=0.2,
                      requestSha256=lab.digest(self.request), responseSha256=lab.digest(response)))
            with patch('urllib.request.urlopen', side_effect=AssertionError('No network allowed')):
                first = lab.report(root, self.cases, self.protocol)
                second = lab.report(root, self.cases, self.protocol)
            self.assertEqual(first['inputTokens'], 123)
            self.assertEqual(first['results'], second['results'])
            response['usage']['input_tokens'] = 999
            lab.write(root / 'R01.response.json', response)
            with self.assertRaises(ValueError):
                lab.report(root, self.cases, self.protocol)

    def test_running_twice_does_not_repeat_successful_requests(self):
        with tempfile.TemporaryDirectory(prefix='jev-cache-test-') as directory:
            root = Path(directory)
            original_root = lab.ROOT
            original_read = lab.read
            def read(path):
                if '/runs/' not in path.as_posix():
                    return original_read(original_root / path.relative_to(root))
                return original_read(path)
            fake_response = io.BytesIO(json.dumps(self.response()).encode())
            fake_response.status = 200
            with patch.object(lab, 'ROOT', root), patch.object(lab, 'read', side_effect=read), \
                    patch.object(lab, 'verify_inputs'), patch.object(lab, 'credentials', return_value=('https://example.test', 'fake')), \
                    patch.object(lab, 'urlopen', return_value=fake_response) as network, \
                    patch.object(lab, 'report'), patch('sys.argv', ['experiment.py', 'run']):
                (root / 'inputs').mkdir()
                (root / 'inputs/frozen.json').write_bytes((original_root / 'inputs/frozen.json').read_bytes())
                one_case_read = read
                def only_first(path):
                    data = one_case_read(path)
                    return data[:1] if path.name == 'cases.json' else data
                with patch.object(lab, 'read', side_effect=only_first):
                    lab.main()
                    lab.main()
                self.assertEqual(network.call_count, 1)


if __name__ == '__main__':
    unittest.main()

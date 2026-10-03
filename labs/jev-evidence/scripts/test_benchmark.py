import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

import benchmark as bench


class BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures, cls.reference, cls.policy = bench.load_suite()

    def response(self, key='R01', choice='supported', relation='supports', confidence=1):
        request = self.fixtures[key]
        answers = {}
        for question_id, question in request['questions'].items():
            label = choice if question_id == 'assessment' else relation
            answers[question_id] = dict(type='choice', choice=label, confidence=confidence,
                probabilities={k: int(k == label) for k in question['criteria']})
        return dict(model=request['model'], answers=answers, usage=dict(input_tokens=100, output_tokens=10))

    def test_coverage_and_separation(self):
        self.assertEqual(len(self.fixtures), 24)
        self.assertEqual({r['expected'] for r in self.reference['cases']}, set(bench.LABELS))
        self.assertEqual(sum(c['origin'] == 'real_extraction' for c in self.reference['cases']), 4)
        self.assertFalse(next(c for c in self.reference['cases'] if c['fixtureId'] == 'R03')['scored'])
        for request in self.fixtures.values():
            self.assertNotIn('rationale', json.dumps(request))
            self.assertNotIn('expected', request['state'])
        self.assertNotEqual(self.fixtures['R04']['state']['externalEvidence'][0]['sourceId'],
                            self.fixtures['F08']['state']['externalEvidence'][0]['sourceId'])

    def test_zero_network_planning_and_saved_calls(self):
        jobs = bench.sequence(self.fixtures, self.policy, 'full', 1)
        with patch.object(bench, 'urlopen', side_effect=AssertionError('No network')):
            diagnostic = bench.plan(self.fixtures, self.reference, self.policy, jobs, 'diagnostic')
            guarded = bench.plan(self.fixtures, self.reference, self.policy, jobs, 'guarded')
        self.assertEqual(diagnostic['plannedHttpCalls'], 24)
        self.assertEqual(guarded['plannedHttpCalls'], 21)
        self.assertFalse(diagnostic['accuracyMeasured'])
        with self.assertRaises(ValueError):
            bench.sequence(self.fixtures, self.policy, 'full', 4)

    def test_preflight_cannot_be_overridden_by_confidence(self):
        for key in ['C03', 'C04', 'F07']:
            guard = bench.guarded_decision(self.fixtures[key], self.response(key), self.policy)
            self.assertEqual(guard['action'], 'abstain')

    def test_high_confidence_and_disagreeing_sources_abstain(self):
        guard = bench.guarded_decision(self.fixtures['R01'], self.response(relation='contradicts'), self.policy)
        self.assertEqual(guard['reason'], 'source_relations_do_not_agree')
        guard = bench.guarded_decision(self.fixtures['R01'], self.response(confidence=.5), self.policy)
        self.assertEqual(guard['reason'], 'low_confidence')

    def test_transport_fixture_contracts(self):
        fixtures = bench.base.read(bench.SUITE / 'transport.json')['cases']
        for fixture in fixtures:
            event = fixture['event']
            with self.subTest(event=event), tempfile.TemporaryDirectory(prefix='jev-v2-test-') as temp:
                directory = Path(temp)
                request = self.fixtures['R01']
                if event == 'interrupted_receipt':
                    bench.base.write(directory / 'R01-r1.receipt.json',
                        dict(status='in_flight', requestSha256=bench.base.digest(request)))
                    with patch.object(bench, 'urlopen') as network, self.assertRaises(ValueError):
                        bench.evaluate_once('https://example.test', 'fake', request, directory, 'R01-r1', 1)
                    network.assert_not_called()
                    continue
                raw = self.response()
                error = None
                if event.startswith('http_'):
                    code = int(event.split('_')[1])
                    error = HTTPError('https://example.test', code, 'fixture', None, None)
                elif event == 'timeout':
                    error = TimeoutError()
                elif event == 'missing_answer':
                    raw['answers'].pop('assessment')
                elif event == 'invented_choice':
                    raw['answers']['assessment']['choice'] = 'invented'
                elif event == 'invalid_probability':
                    raw['answers']['assessment']['probabilities']['supported'] = -1
                elif event == 'model_drift':
                    raw['model'] = 'jev-synthetic-new-version'
                body = b'{not-json' if event == 'invalid_json' else json.dumps(raw).encode()
                stream = io.BytesIO(body)
                stream.status = 200
                with patch.object(bench, 'urlopen', side_effect=error, return_value=stream) as network:
                    receipt = bench.evaluate_once('https://example.test', 'fake', request, directory, 'R01-r1', 1)
                    self.assertEqual(network.call_count, 1)
                    self.assertNotEqual(receipt['status'], 'completed')
                    with self.assertRaises(ValueError):
                        bench.evaluate_once('https://example.test', 'fake', request, directory, 'R01-r1', 1)
                    self.assertEqual(network.call_count, 1)
                if not error:
                    self.assertEqual((directory / 'R01-r1.response.json').read_bytes(), body)

    def test_idempotency_and_offline_replay(self):
        with tempfile.TemporaryDirectory(prefix='jev-v2-cache-test-') as temp:
            directory = Path(temp)
            raw = self.response()
            stream = io.BytesIO(json.dumps(raw).encode())
            stream.status = 200
            with patch.object(bench, 'urlopen', return_value=stream) as network:
                bench.evaluate_once('https://example.test', 'fake', self.fixtures['R01'], directory, 'R01-r1', 1)
                bench.evaluate_once('https://example.test', 'fake', self.fixtures['R01'], directory, 'R01-r1', 1)
                self.assertEqual(network.call_count, 1)
            with patch.object(bench, 'urlopen', side_effect=AssertionError('No network')):
                summary = bench.summarize(directory, self.fixtures, self.reference, self.policy, [('R01-r1', 'R01'), ('R02-r1', 'R02')])
            self.assertEqual(summary['completed'], 1)
            self.assertEqual(summary['notAttempted'], 1)
            self.assertEqual(summary['knownInputTokens'], 100)
            self.assertEqual(summary['real']['correct'], 1)
            self.assertIsNone(summary['controls']['agreementRate'])
            (directory / 'R01-r1.response.json').write_text('{}')
            with self.assertRaises(ValueError):
                bench.summarize(directory, self.fixtures, self.reference, self.policy, [('R01-r1', 'R01')])

    def test_failures_stay_unknown_not_zero_cost(self):
        with tempfile.TemporaryDirectory(prefix='jev-v2-unknown-test-') as temp:
            directory = Path(temp)
            with patch.object(bench, 'urlopen', side_effect=TimeoutError()):
                bench.evaluate_once('https://example.test', 'fake', self.fixtures['R01'], directory, 'R01-r1', 1)
            summary = bench.summarize(directory, self.fixtures, self.reference, self.policy, [('R01-r1', 'R01')])
            self.assertEqual(summary['unknownConsumption'], ['R01-r1'])
            self.assertIsNone(summary['latency']['p50Seconds'])
            self.assertIsNone(summary['real']['agreementRate'])

    def test_confident_wrong_answer_remains_visible(self):
        rows = [dict(status='completed', scored=True, expected='insufficient', choice='supported',
                     correct=False, guard=dict(action='experimental_candidate'))]
        metrics = bench.metric_group(rows)
        self.assertEqual(metrics['falseSupport'], 1)
        self.assertEqual(metrics['candidateErrors'], 1)
        self.assertEqual(metrics['candidatePrecision'], 0)


if __name__ == '__main__':
    unittest.main()

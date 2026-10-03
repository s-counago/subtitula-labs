import copy
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import luna_benchmark as luna
import local_retrieval as retrieval
import subscription_transport as transport
import subscription_transport_v2 as transport_v2


class LunaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures, cls.reference, cls.policy = luna.baseline.load_suite()

    def payload(self, key='R01'):
        return {k: copy.deepcopy(self.fixtures[key][k]) for k in ('state', 'questions')}

    def response(self, key='R01', label='supported', relation='supports'):
        sources = self.payload(key)['state']['externalEvidence']
        return dict(assessment=label, sourceRelations={s['sourceId']: relation for s in sources},
            rationale='Respuesta sintética de test.', missingEvidence=[],
            evidenceQuotes=[dict(sourceId=sources[0]['sourceId'], quote=sources[0]['excerpt'])] if sources else [])

    def test_contract_rejects_invented_label_and_source(self):
        response = self.response()
        luna.validate_response(response, self.payload())
        response['assessment'] = 'true'
        with self.assertRaises(ValueError):
            luna.validate_response(response, self.payload())
        response = self.response()
        response['sourceRelations']['invented'] = 'supports'
        with self.assertRaises(ValueError):
            luna.validate_response(response, self.payload())

    def test_no_fabricated_confidence_or_reference_in_payload(self):
        for key in self.fixtures:
            payload = self.payload(key)
            self.assertEqual(set(payload), {'state', 'questions'})
            self.assertNotIn('rationale', payload['state'])
            self.assertNotIn('expected', payload['state'])
            self.assertNotIn('confidence', luna.output_schema(payload)['properties'])
            self.assertNotIn('probabilities', luna.output_schema(payload)['properties'])

    def test_nonliteral_citation_abstains_without_hiding_assessment(self):
        response = self.response()
        response['evidenceQuotes'][0]['quote'] = 'Una cita inventada que no aparece en el documento.'
        luna.validate_response(response, self.payload())
        self.assertEqual(luna.guard(self.payload(), response)['reason'], 'missing_or_nonliteral_citation')
        self.assertEqual(response['assessment'], 'supported')

    def test_guards_detect_missing_reports_period_and_disagreement(self):
        for key in ('C03', 'C04', 'F07', 'F04'):
            self.assertEqual(luna.guard(self.payload(key), self.response(key))['action'], 'abstain')
        response = self.response(relation='contradicts')
        self.assertEqual(luna.guard(self.payload(), response)['reason'], 'source_relations_do_not_agree')
        self.assertEqual(luna.guard(self.payload(), self.response())['action'], 'experimental_candidate')

    def test_retrieval_uses_text_and_deterministic_document_diversity(self):
        chunks = [dict(sourceId='A1', documentId='A', title='Documento', excerpt='alquiler vivienda presupuesto'),
            dict(sourceId='A2', documentId='A', title='Documento', excerpt='alquiler alquiler vivienda'),
            dict(sourceId='B1', documentId='B', title='Documento', excerpt='alquiler vivienda'),
            dict(sourceId='C1', documentId='C', title='Documento', excerpt='residuos tratamiento')]
        selected = retrieval.retrieve('alquiler vivienda', chunks, limit=2, per_document=1)
        self.assertEqual({c['documentId'] for c in selected}, {'A', 'B'})
        self.assertEqual(selected, retrieval.retrieve('alquiler vivienda', list(reversed(chunks)), limit=2, per_document=1))
        self.assertEqual(retrieval.retrieve('astronomia', chunks), [])

    def test_corpus_ignores_manually_selected_excerpt(self):
        source = dict(sourceId='D01', title='Example', snapshot='sources/example.pdf', snapshotSha256='fake',
                      excerpt='LEAKED REFERENCE PASSAGE')
        with patch.object(retrieval, 'document_pages', return_value=[('PDF p. 1', 'Texto completo obtenido del documento')]):
            corpus = retrieval.build_corpus([source])
        self.assertNotIn('LEAKED', json.dumps(corpus))
        self.assertIn('Texto completo', corpus['chunks'][0]['excerpt'])

    def test_retrieved_payload_does_not_inherit_unretrieved_arithmetic(self):
        payload = luna.retrieved_payload(self.fixtures['R04'], [])
        self.assertNotIn('arithmetic', payload['state'])
        self.assertEqual(payload['state']['externalEvidence'], [])
        self.assertEqual(set(payload['questions']), {'assessment'})

    def test_html_extraction_excludes_navigation_and_scripts(self):
        parser = retrieval.VisibleHTML()
        parser.feed('<html><head><title>Hidden</title></head><body><nav><span>Navigation</span></nav><script>Hidden</script><p>Budget &amp; evidence</p></body></html>')
        self.assertEqual(' '.join(parser.parts), 'Budget & evidence')

    def test_subscription_environment_excludes_alternative_auth(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'fake', 'CODEX_API_KEY': 'fake', 'CODEX_ACCESS_TOKEN': 'fake', 'OPENAI_BASE_URL': 'https://example.test'}):
            environment = transport.subscription_environment()
        self.assertFalse({'OPENAI_API_KEY', 'CODEX_API_KEY', 'CODEX_ACCESS_TOKEN', 'OPENAI_BASE_URL'} & set(environment))
        command = transport.build_command('codex', Path('C:/example'), Path('C:/empty'), dict(model='gpt-5.6-luna', reasoningEffort='xhigh'))
        self.assertIn('forced_login_method="chatgpt"', command)
        self.assertIn('--ignore-user-config', command)
        self.assertIn('plugins', command)
        self.assertIn('multi_agent', command)
        self.assertIn('web_search="disabled"', command)

    def test_transport_rejects_tools_failure_and_missing_usage(self):
        event = dict(type='turn.completed', usage=dict(input_tokens=100, output_tokens=10))
        self.assertEqual(transport.validate_events([event], 0, True), event['usage'])
        for events in [[event, dict(type='item.completed', item=dict(type='command_execution'))],
                       [event, dict(type='turn.failed')], [dict(type='turn.completed')], [event, event]]:
            with self.assertRaises(ValueError):
                transport.validate_events(events, 0, True)

    def test_subscription_login_check_uses_supported_command(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(transport_v2.shutil, 'which', return_value='codex'), \
                 patch.object(transport_v2.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout='Logged in using ChatGPT', stderr='')) as login, \
                 patch.object(transport_v2.subprocess, 'Popen', side_effect=RuntimeError('stop before network')):
                with self.assertRaises(RuntimeError):
                    transport_v2.infer(self.payload(), luna.output_schema(self.payload()), luna.INSTRUCTIONS,
                        Path(temp), dict(model='gpt-5.6-luna', reasoningEffort='xhigh'))
            self.assertEqual(login.call_args.args[0], ['codex', 'login', 'status'])

    def temporary_inputs(self, suite):
        luna.base.write(suite/'requests/curated-R01.json', self.payload())
        luna.base.write(suite/'schemas/curated-R01.json', luna.output_schema(self.payload()))
        (suite/'instructions.txt').write_text(luna.INSTRUCTIONS)

    def fake_infer(self, payload, schema, instructions, target, config):
        response = self.response()
        luna.base.write(target/'final.json', response)
        (target/'events.jsonl').write_text(json.dumps(dict(type='turn.completed', usage=dict(input_tokens=100, output_tokens=10)))+'\n')
        return response, dict(seconds=1, usage=dict(input_tokens=100, output_tokens=10))

    def test_cached_success_is_not_repeated_and_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            suite = Path(temp)/'suite'
            self.temporary_inputs(suite)
            directory = Path(temp)/'run'
            with patch.object(luna, 'SUITE', suite), patch.object(transport, 'infer', side_effect=self.fake_infer) as infer:
                job = dict(jobId='curated-R01')
                config = dict(model='gpt-5.6-luna', reasoningEffort='xhigh', billing='chatgpt_subscription_limits')
                first = luna.evaluate_once(job, directory, config)
                self.assertEqual(first['status'], 'completed')
                luna.evaluate_once(job, directory, config)
                self.assertEqual(infer.call_count, 1)
                (directory/'curated-R01/final.json').write_text('{}')
                with self.assertRaises(ValueError):
                    luna.evaluate_once(job, directory, config)

    def test_uncertain_failure_is_not_resent(self):
        with tempfile.TemporaryDirectory() as temp:
            suite = Path(temp)/'suite'
            self.temporary_inputs(suite)
            with patch.object(luna, 'SUITE', suite), patch.object(transport, 'infer', side_effect=RuntimeError('synthetic timeout')) as infer:
                job = dict(jobId='curated-R01')
                config = dict(model='gpt-5.6-luna', reasoningEffort='xhigh', billing='chatgpt_subscription_limits')
                receipt = luna.evaluate_once(job, Path(temp)/'run', config)
                self.assertEqual(receipt['status'], 'failed_or_uncertain')
                self.assertNotIn('usage', receipt)
                with self.assertRaises(ValueError):
                    luna.evaluate_once(job, Path(temp)/'run', config)
                self.assertEqual(infer.call_count, 1)

    def test_wrong_assessments_and_unscored_reference_remain_separate(self):
        rows = [dict(status='completed', scored=True, expected='insufficient', assessment='supported',
                     correct=False, guard=dict(action='abstain')),
                dict(status='completed', scored=False, expected='supported', assessment='contradicted',
                     correct=False, guard=dict(action='experimental_candidate'))]
        metrics = luna.group_metrics(rows)
        self.assertEqual(metrics['scored'], 1)
        self.assertEqual(metrics['falseSupport'], 1)
        self.assertEqual(metrics['falseContradiction'], 0)
        self.assertEqual(metrics['candidateCount'], 0)
        self.assertIsNone(metrics['candidatePrecision'])


if __name__ == '__main__':
    unittest.main()

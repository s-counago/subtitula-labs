"""Run the unchanged v1 workflow with subscription-authenticated Codex CLI/Luna."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from unittest.mock import patch

import pipeline
from common import ROOT, now, read_json, sha, write_json
from contracts import EXTRACTION_SCHEMA, validate_shape

CONFIG_PATH = ROOT / 'config/luna-experiment.json'
DISABLED_FEATURES = ['shell_tool', 'unified_exec', 'apps', 'browser_use',
    'computer_use', 'in_app_browser', 'image_generation', 'multi_agent',
    'memories', 'hooks', 'skill_mcp_dependency_install', 'skill_search',
    'goals', 'sleep_tool', 'view_image', 'workspace_dependencies']

def subscription_environment():
    # Let the official CLI handle its existing login. Never extract its tokens.
    env = os.environ.copy()
    for name in list(env):
        if name.upper() in {'OPENAI_API_KEY', 'CODEX_API_KEY', 'OPENAI_BASE_URL'}:
            del env[name]
    return env

def run_codex(stage, prompt, payload, schema, target, config):
    """One fresh CLI session; save output and stop on uncertain/failed outcomes."""
    target.mkdir(parents=True, exist_ok=True)
    schema_path = target / 'schema.json'
    instructions_path = target / 'instructions.txt'
    final_path = target / 'final.json'
    events_path = target / 'events.jsonl'
    stderr_path = target / 'stderr.txt'
    write_json(schema_path, schema)
    instructions_path.write_text(prompt, encoding='utf-8')
    payload_text = json.dumps(payload, ensure_ascii=False)
    (target / 'input.json').write_text(payload_text, encoding='utf-8')
    executable = shutil.which('codex')
    if not executable:
        raise RuntimeError('Codex CLI is not installed.')
    # A new empty working directory prevents project discovery from the lab.
    working = Path(tempfile.mkdtemp(prefix='claims-luna-'))
    command = [executable, 'exec', '--ignore-user-config', '--ephemeral',
        '--skip-git-repo-check', '--sandbox', 'read-only', '--json', '--color', 'never',
        '--model', config['model'], '--cd', str(working),
        '--output-schema', str(schema_path), '--output-last-message', str(final_path),
        '-c', 'forced_login_method="chatgpt"',
        '-c', 'model_reasoning_effort=' + json.dumps(config['reasoningEffort']),
        '-c', 'model_instructions_file=' + json.dumps(instructions_path.as_posix()),
        '-c', 'project_doc_max_bytes=0', '-c', 'skills.max_context_tokens=1',
        '-c', 'web_search="disabled"', '-c', 'approval_policy="never"',
        '-c', 'features.skip_host_skill_discovery=true']
    for feature in DISABLED_FEATURES:
        command.extend(['--disable', feature])
    command.append('-')
    write_json(target / 'invocation.json', {'argv': command, 'stage': stage,
        'auth': 'existing_chatgpt_login', 'workingDirectoryContainsCorpus': False,
        'inputSha256': sha(target / 'input.json'), 'schemaSha256': sha(schema_path),
        'instructionsSha256': sha(instructions_path)})
    started = time.monotonic()
    try:
        with events_path.open('wb') as events_file, stderr_path.open('wb') as error_file:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=events_file,
                stderr=error_file, cwd=working, env=subscription_environment(),
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            try:
                process.communicate(payload_text.encode('utf-8'), timeout=config['requestTimeoutSeconds'])
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                raise RuntimeError('Codex timed out; outcome uncertain, no automatic retry.') from None
    finally:
        # Remove only this verified, empty scratch directory; never recursively.
        try:
            working.rmdir()
        except OSError:
            pass
    events = []
    for line in events_path.read_text(encoding='utf-8').splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            raise RuntimeError('CLI returned a non-JSON event; inspect preserved output.') from None
    tool_items = [event.get('item', {}) for event in events
        if event.get('type', '').startswith('item.') and
        event.get('item', {}).get('type') not in {'agent_message', 'reasoning', 'error'}]
    completed = [event for event in events if event.get('type') == 'turn.completed']
    if process.returncode != 0 or not final_path.exists() or len(completed) != 1:
        raise RuntimeError('Codex did not complete one turn; inspect preserved events and stderr.')
    if tool_items:
        raise RuntimeError('Unexpected tool activity; result excluded from comparison.')
    parsed = read_json(final_path)
    validate_shape(parsed, schema)
    usage = completed[0].get('usage', {})
    receipt = {'stage': stage, 'finishedAt': now(),
        'elapsedSeconds': round(time.monotonic() - started, 3), 'state': 'completed',
        'exitCode': process.returncode, 'reportedCodexUsage': usage,
        'usage': {'prompt_tokens': usage.get('input_tokens', 0),
            'completion_tokens': usage.get('output_tokens', 0),
            'total_tokens': usage.get('input_tokens', 0) + usage.get('output_tokens', 0)},
        'toolItemCount': len(tool_items), 'responseSha256': sha(final_path),
        'eventsSha256': sha(events_path), 'billing': 'chatgpt_subscription_limits',
        'runtimeWarnings': [e['item']['message'] for e in events
            if e.get('item', {}).get('type') == 'error']}
    return parsed, receipt

class CodexRunner(pipeline.Runner):
    def __init__(self, config, frozen):
        super().__init__(config, frozen)
        manifest = read_json(self.manifest_path)
        adapter_hashes = {p: sha(ROOT / p) for p in
            ['scripts/luna_pipeline.py', 'config/luna-experiment.json']}
        if manifest.get('adapterHashes', adapter_hashes) != adapter_hashes:
            raise RuntimeError('Adapter changed. Start another run.')
        manifest.update({'adapterHashes': adapter_hashes, 'transport': 'codex_exec',
            'codexVersion': subprocess.check_output(['codex', '--version'], text=True).strip(),
            'authMethod': 'chatgpt_subscription', 'reasoningEffort': config['reasoningEffort'],
            'baselineExperimentId': 'vigo-2025-12-23-v1',
            'comparisonLimits': ['Codex adds runtime context to the unchanged task instructions.',
                'Luna uses low reasoning; GLM used thinking disabled.',
                'Codex CLI does not expose the same temperature, seed or output-token cap.',
                'Schema item limits, context rules, validators and workflow are unchanged.']})
        write_json(self.manifest_path, manifest)

    def infer(self, stage, prompt, payload, schema):
        request = {'model': self.config['model'], 'instructions': prompt,
            'payload': payload, 'schema': schema, 'reasoningEffort': self.config['reasoningEffort']}
        request_path = self.path / 'requests' / (stage + '.json')
        response_path = self.path / 'responses' / (stage + '.json')
        receipt_path = self.path / 'receipts' / (stage + '.json')
        if request_path.exists() and read_json(request_path) != request:
            raise RuntimeError('Saved request differs; preserve this run.')
        if response_path.exists():
            if not receipt_path.exists() or read_json(receipt_path)['state'] != 'completed':
                raise RuntimeError('Response has no completed receipt.')
            parsed = read_json(response_path)
        else:
            if receipt_path.exists():
                raise RuntimeError('Unfinished operation exists; no automatic retry.')
            if len(list((self.path / 'receipts').glob('*.json'))) >= self.config['maxModelRequests']:
                raise RuntimeError('Request budget reached.')
            write_json(request_path, request)
            receipt = {'stage': stage, 'startedAt': now(), 'state': 'sending',
                'requestSha256': sha(request_path)}
            write_json(receipt_path, receipt)
            print(json.dumps({'stage': stage, 'state': 'sending', 'model': self.config['model']}), flush=True)
            try:
                parsed, completed = run_codex(stage, prompt, payload, schema,
                    self.path / 'transport' / stage, self.config)
                write_json(response_path, parsed)
                receipt.update(completed)
                receipt['responseSha256'] = sha(response_path)
                write_json(receipt_path, receipt)
            except Exception as error:
                receipt.update({'state': 'failed_or_uncertain', 'finishedAt': now(),
                    'errorType': type(error).__name__, 'error': str(error)[:250]})
                write_json(receipt_path, receipt)
                raise RuntimeError('Luna operation did not complete; no automatic retry.') from error
            print(json.dumps({'stage': stage, 'state': 'completed',
                'seconds': receipt['elapsedSeconds'], 'usage': receipt['reportedCodexUsage']}), flush=True)
        validate_shape(parsed, schema)
        write_json(self.path / 'parsed' / (stage + '.json'), parsed)
        return parsed

    def persist(self):
        summary = super().persist()
        receipts = [read_json(p) for p in (self.path / 'receipts').glob('*.json')]
        total = {key: sum(r.get('reportedCodexUsage', {}).get(key, 0) for r in receipts)
            for key in ['input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens']}
        # API prices are counterfactual here. Actual billing uses subscription limits.
        summary.pop('estimatedGenerationCostUsdFromReportedTokens', None)
        summary.update({'reportedCodexUsage': total, 'billing': 'chatgpt_subscription_limits',
            'actualApiChargeUsd': None, 'apiPriceEquivalentUsd':
            ((total['input_tokens'] - total['cached_input_tokens']) * 0.20 +
             total['cached_input_tokens'] * 0.02 + total['output_tokens'] * 1.20) / 1_000_000,
            'apiEquivalentIsCharge': False,
            'apiEquivalentLimit': 'Uses CLI token counts including runtime context; not a measured API request.'})
        write_json(self.path / 'summary.json', summary)
        return summary

def main():
    args = argparse.ArgumentParser()
    args.add_argument('--preflight', action='store_true')
    args.add_argument('--offline', action='store_true')
    options = args.parse_args()
    config = read_json(CONFIG_PATH)
    if options.preflight:
        target = ROOT / 'runs/luna-transport-preflight'
        if (target / 'events.jsonl').exists():
            raise RuntimeError('Preflight already attempted; inspect saved files first.')
        parsed, receipt = run_codex('preflight', 'Devuelve listas vacías en el esquema solicitado.',
            {'purpose': 'transport_and_schema_check_no_corpus'}, EXTRACTION_SCHEMA, target, config)
        write_json(target / 'receipt.json', receipt)
        print(json.dumps({'state': receipt['state'], 'usage': receipt['reportedCodexUsage'],
            'toolItems': receipt['toolItemCount']}))
        return
    def routed_read(path):
        return config if Path(path) == ROOT / 'config/experiment.json' else read_json(path)
    with patch.object(pipeline, 'Runner', CodexRunner), patch.object(pipeline, 'read_json', routed_read):
        if options.offline:
            with patch(__name__ + '.run_codex', side_effect=RuntimeError('Network prohibited during replay')):
                pipeline.main()
        else:
            pipeline.main()

if __name__ == '__main__':
    main()

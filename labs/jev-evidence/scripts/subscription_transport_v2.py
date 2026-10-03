import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

import experiment as base

DISABLED_FEATURES = ['shell_tool', 'unified_exec', 'apps', 'plugins', 'remote_plugin',
    'browser_use', 'browser_use_external', 'computer_use', 'in_app_browser', 'image_generation',
    'multi_agent', 'multi_agent_v2', 'memories', 'hooks', 'skill_mcp_dependency_install',
    'skill_search', 'goals', 'sleep_tool', 'view_image', 'workspace_dependencies', 'code_mode',
    'code_mode_host', 'unbounded_connection_retries']


def subscription_environment():
    excluded = {'OPENAI_API_KEY', 'CODEX_API_KEY', 'OPENAI_BASE_URL', 'CODEX_ACCESS_TOKEN'}
    return {key: value for key, value in os.environ.items() if key.upper() not in excluded}


def build_command(executable, target, working, config):
    command = [executable, 'exec', '--ignore-user-config', '--ephemeral', '--skip-git-repo-check',
        '--sandbox', 'read-only', '--json', '--color', 'never', '--model', config['model'],
        '--cd', str(working), '--output-schema', str(target / 'schema.json'),
        '--output-last-message', str(target / 'final.json'),
        '-c', 'forced_login_method="chatgpt"',
        '-c', 'model_reasoning_effort='+json.dumps(config['reasoningEffort']),
        '-c', 'model_instructions_file='+json.dumps((target / 'instructions.txt').as_posix()),
        '-c', 'project_doc_max_bytes=0', '-c', 'skills.max_context_tokens=1',
        '-c', 'web_search="disabled"', '-c', 'approval_policy="never"',
        '-c', 'features.skip_host_skill_discovery=true']
    for feature in DISABLED_FEATURES:
        command.extend(['--disable', feature])
    return command+['-']


def validate_events(events, exit_code, final_exists):
    completed = [event for event in events if event.get('type') == 'turn.completed']
    forbidden = [event for event in events if event.get('type', '').startswith('item.')
                 and event.get('item', {}).get('type') not in ('agent_message', 'reasoning', 'error')]
    failed = any(event.get('type') == 'turn.failed' for event in events)
    if exit_code != 0 or len(completed) != 1 or not final_exists or forbidden or failed:
        raise ValueError('CLI did not produce one isolated, tool-free completed evaluation')
    usage = completed[0].get('usage', {})
    if any(type(usage.get(k)) is not int or usage[k] < 0 for k in ('input_tokens', 'output_tokens')):
        raise ValueError('Missing measured usage')
    return usage


def infer(payload, schema, instructions, target, config):
    target.mkdir(parents=True, exist_ok=True)
    target = target.resolve()
    base.write(target / 'input.json', payload)
    base.write(target / 'schema.json', schema)
    (target / 'instructions.txt').write_text(instructions, encoding='utf-8')
    executable = shutil.which('codex')
    if not executable:
        raise RuntimeError('Codex CLI unavailable')
    environment = subscription_environment()
    login = subprocess.run([executable, 'login', 'status'],
        capture_output=True, text=True, env=environment, timeout=20)
    if login.returncode or 'Logged in using ChatGPT' not in login.stdout+login.stderr:
        raise RuntimeError('An existing ChatGPT subscription login is required')
    working = Path(tempfile.mkdtemp(prefix='jev-luna-isolated-'))
    command = build_command(executable, target, working, config)
    base.write(target / 'invocation.json', dict(argv=command, auth='existing_chatgpt_login',
        referenceAvailable=False, toolsAllowed=False, modelRequested=config['model'],
        modelVerification='CLI requested model; exec event stream does not attest resolved backend snapshot'))
    started = time.perf_counter()
    try:
        with (target / 'events.jsonl').open('wb') as stdout, (target / 'stderr.txt').open('wb') as stderr:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
                cwd=working, env=environment,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            try:
                process.communicate(base.encoded(payload), timeout=config['timeoutSeconds'])
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                raise RuntimeError('Timeout; outcome uncertain, no automatic retry') from None
    finally:
        try:
            working.rmdir()
        except OSError:
            pass
    events = [json.loads(line) for line in (target / 'events.jsonl').read_text(encoding='utf-8').splitlines()]
    usage = validate_events(events, process.returncode, (target / 'final.json').exists())
    return base.read(target / 'final.json'), dict(seconds=round(time.perf_counter()-started, 6),
        usage=usage, exitCode=process.returncode, toolItemCount=0,
        runtimeWarnings=[event.get('item', {}).get('message') for event in events if event.get('item', {}).get('type') == 'error'])

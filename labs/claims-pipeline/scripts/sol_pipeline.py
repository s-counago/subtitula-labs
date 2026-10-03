"""Same frozen v1 pipeline and Codex transport, with Sol medium configuration."""
from pathlib import Path
from unittest.mock import patch
import pipeline
from pipeline import Runner as OriginalRunner
from luna_pipeline import CodexRunner
from common import ROOT, read_json, sha, write_json

CONFIG_PATH = ROOT / 'config/sol-experiment.json'


class SolRunner(CodexRunner):
    def __init__(self, config, frozen):
        super().__init__(config, frozen)
        manifest = read_json(self.manifest_path)
        hashes = {name: sha(ROOT / name) for name in [
            'scripts/sol_pipeline.py', 'config/sol-experiment.json',
            'config/luna-xhigh-long-experiment.json']}
        if manifest.get('variantHashes', hashes) != hashes:
            raise RuntimeError('Sol configuration changed; preserve this run.')
        manifest.update({
            'variantHashes': hashes,
            'configurationPath': CONFIG_PATH.relative_to(ROOT).as_posix(),
            'comparisonExperimentIds': ['vigo-2025-12-23-luna-v1', 'vigo-2025-12-23-luna-xhigh-v1b'],
            'changedInferenceParameters': {
                'model': {'from': 'gpt-5.6-luna', 'to': config['model']},
                'reasoningEffort': {'from': ['low', 'xhigh'], 'to': config['reasoningEffort']}},
            'requestTimeoutSeconds': config['requestTimeoutSeconds'],
            'generationPipelineChanged': False,
            'comparisonLimits': [
                'Same frozen v1 extraction, context recovery, schemas, validators, matter resolution and persistence.',
                'Same official Codex transport and existing ChatGPT subscription login.',
                'Model and reasoning effort change; API price metadata changes only for accounting.',
                'The local wait limit is 900 seconds, equal to completed Luna xhigh and above Luna low 360 seconds.',
                'One completed run per setting cannot estimate stochastic variation.',
                'The frozen reference was not included in inference requests.']})
        write_json(self.manifest_path, manifest)

    def persist(self):
        # Preserve original persistence; replace only the Luna-specific price accounting.
        summary = OriginalRunner.persist(self)
        receipts = [read_json(p) for p in (self.path / 'receipts').glob('*.json')]
        keys = ['input_tokens', 'cached_input_tokens', 'cache_write_input_tokens',
                'output_tokens', 'reasoning_output_tokens']
        total = {key: sum(r.get('reportedCodexUsage', {}).get(key, 0) for r in receipts) for key in keys}
        normal = total['input_tokens'] - total['cached_input_tokens'] - total['cache_write_input_tokens']
        equivalent = (normal * self.config['pricePerMillionInputTokens']
            + total['cached_input_tokens'] * self.config['pricePerMillionCachedInputTokens']
            + total['cache_write_input_tokens'] * self.config['pricePerMillionInputTokens'] * 1.25
            + total['output_tokens'] * self.config['pricePerMillionOutputTokens']) / 1_000_000
        summary.pop('estimatedGenerationCostUsdFromReportedTokens', None)
        summary.update({'reportedCodexUsage': total, 'billing': 'chatgpt_subscription_limits',
            'actualApiChargeUsd': None, 'apiPriceEquivalentUsd': equivalent,
            'apiEquivalentIsCharge': False,
            'apiEquivalentLimit': 'Uses CLI token counts including runtime context; not a measured API request.'})
        write_json(self.path / 'summary.json', summary)
        return summary


def main():
    config = read_json(CONFIG_PATH)
    high = read_json(ROOT / 'config/luna-xhigh-long-experiment.json')
    changed = {key for key in set(config) | set(high) if config.get(key) != high.get(key)}
    assert changed == {'experimentId', 'model', 'reasoningEffort',
        'pricePerMillionInputTokens', 'pricePerMillionOutputTokens',
        'pricePerMillionCachedInputTokens', 'priceSource', 'priceCheckedOn'}, changed
    assert config['model'] == 'gpt-5.6-sol' and config['reasoningEffort'] == 'medium'

    def routed_read(path):
        return config if Path(path) == ROOT / 'config/experiment.json' else read_json(path)

    with patch.object(pipeline, 'Runner', SolRunner), patch.object(pipeline, 'read_json', routed_read):
        pipeline.main()


if __name__ == '__main__':
    main()

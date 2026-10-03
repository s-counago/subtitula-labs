"""Repeat the saved Luna low experiment, changing only reasoning effort and run ID."""
from pathlib import Path
from unittest.mock import patch
import pipeline
from luna_pipeline import CodexRunner
from common import ROOT, read_json, sha, write_json

CONFIG_PATH = ROOT / 'config/luna-xhigh-experiment.json'

class XHighRunner(CodexRunner):
    def __init__(self, config, frozen):
        super().__init__(config, frozen)
        manifest = read_json(self.manifest_path)
        variant_hashes = {p: sha(ROOT / p) for p in
            ['scripts/luna_xhigh.py', 'config/luna-xhigh-experiment.json']}
        if manifest.get('variantHashes', variant_hashes) != variant_hashes:
            raise RuntimeError('Variant changed. Preserve the existing run.')
        manifest.update({'variantHashes': variant_hashes,
            'comparisonExperimentId': 'vigo-2025-12-23-luna-v1',
            'changedInferenceParameter': {'reasoningEffort': {'from': 'low', 'to': 'xhigh'}},
            'comparisonLimits': ['Same Codex transport, model, task instructions, schemas and workflow as Luna low.',
                'A fresh inference is stochastic; one run per effort does not measure variance.',
                'Later context and resolution inputs depend on each run output.']})
        write_json(self.manifest_path, manifest)

def main():
    config = read_json(CONFIG_PATH)
    low = read_json(ROOT / 'config/luna-experiment.json')
    differences = {key for key in set(config) | set(low) if config.get(key) != low.get(key)}
    assert differences == {'experimentId', 'reasoningEffort'}
    assert config['reasoningEffort'] == 'xhigh'
    def routed_read(path):
        return config if Path(path) == ROOT / 'config/experiment.json' else read_json(path)
    with patch.object(pipeline, 'Runner', XHighRunner), patch.object(pipeline, 'read_json', routed_read):
        pipeline.main()

if __name__ == '__main__':
    main()

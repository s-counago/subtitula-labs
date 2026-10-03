"""Versioned Luna effort experiment with an explicitly selected local config."""
import argparse
from pathlib import Path
from unittest.mock import patch
import pipeline
from luna_pipeline import CodexRunner
from common import ROOT, read_json, sha, write_json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    args = parser.parse_args()
    config_path = (ROOT / args.config).resolve()
    config_path.relative_to(ROOT / 'config')
    config = read_json(config_path)
    low = read_json(ROOT / 'config/luna-experiment.json')
    differences = {key for key in set(config) | set(low) if config.get(key) != low.get(key)}
    assert differences == {'experimentId', 'reasoningEffort', 'requestTimeoutSeconds'}
    assert config['reasoningEffort'] == 'xhigh'

    class VariantRunner(CodexRunner):
        def __init__(self, configuration, frozen):
            super().__init__(configuration, frozen)
            manifest = read_json(self.manifest_path)
            variant_hashes = {'scripts/luna_variant.py': sha(ROOT / 'scripts/luna_variant.py'),
                config_path.relative_to(ROOT).as_posix(): sha(config_path)}
            if manifest.get('variantHashes', variant_hashes) != variant_hashes:
                raise RuntimeError('Variant inputs changed; preserve the run.')
            manifest.update({'variantHashes': variant_hashes,
                'configurationPath': config_path.relative_to(ROOT).as_posix(),
                'comparisonExperimentId': 'vigo-2025-12-23-luna-v1',
                'previousInterruptedExperimentId': 'vigo-2025-12-23-luna-xhigh-v1',
                'changedInferenceParameter': {'reasoningEffort': {'from': 'low', 'to': 'xhigh'}},
                'requestTimeoutSeconds': configuration['requestTimeoutSeconds'],
                'comparisonLimits': ['Same Codex transport, task instructions, schemas and workflow as Luna low.',
                    'The local wait limit is extended from 360 to 900 seconds; no sampling budget is changed.',
                    'One earlier xhigh attempt timed out without reported usage; its consumption is unknown.',
                    'One completed run per effort cannot estimate stochastic variation.']})
            write_json(self.manifest_path, manifest)

    def routed_read(path):
        return config if Path(path) == ROOT / 'config/experiment.json' else read_json(path)
    with patch.object(pipeline, 'Runner', VariantRunner), patch.object(pipeline, 'read_json', routed_read):
        pipeline.main()

if __name__ == '__main__':
    main()

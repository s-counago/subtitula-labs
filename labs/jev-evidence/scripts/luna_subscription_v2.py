import sys

import luna_benchmark as experiment
import subscription_transport_v2 as transport


def main():
    experiment.SUITE = experiment.ROOT / 'alternatives/luna-v2'
    experiment.transport = transport
    experiment.main()
    if len(sys.argv) > 1 and sys.argv[1] == 'prepare':
        path = experiment.SUITE / 'manifest.json'
        manifest = experiment.base.read(path)
        for name in ['scripts/luna_subscription_v2.py', 'scripts/subscription_transport_v2.py']:
            manifest['dependencies'][name] = experiment.sha(experiment.ROOT / name)
        manifest['transportCorrection'] = 'Use codex login status without exec-only flag; v1 stopped during local login check before any model invocation.'
        experiment.base.write(path, manifest)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError, OSError) as error:
        raise SystemExit(str(error))

import json
from pathlib import Path

import luna_benchmark as lab
import subscription_transport_v2 as transport


def main():
    lab.SUITE = lab.ROOT / 'alternatives/luna-v2'
    jobs, config = lab.verify()
    directory = lab.ROOT / 'runs/luna-subscription-v2'
    summary = lab.base.read(directory/'summary.json')
    fixtures, reference, policy = lab.baseline.load_suite()
    passed = []
    total = {}
    for job in jobs:
        name = job['jobId']
        payload = lab.base.read(lab.SUITE/'requests'/(name+'.json'))
        if job['track'] == 'curated':
            original = fixtures[job['fixtureId']]
            assert payload == {key: original[key] for key in ('state', 'questions')}
        target = directory/name
        receipt = lab.base.read(target/'receipt.json')
        assert receipt['status'] == 'completed'
        assert receipt['requestSha256'] == lab.sha(lab.SUITE/'requests'/(name+'.json'))
        assert receipt['responseSha256'] == lab.sha(target/'final.json')
        assert receipt['eventsSha256'] == lab.sha(target/'events.jsonl')
        events = [json.loads(line) for line in (target/'events.jsonl').read_text(encoding='utf-8').splitlines()]
        usage = transport.validate_events(events, receipt['exitCode'], True)
        assert usage == receipt['usage']
        invocation = lab.base.read(target/'invocation.json')
        assert invocation['modelRequested'] == config['model']
        assert invocation['auth'] == 'existing_chatgpt_login'
        assert invocation['referenceAvailable'] is False
        assert 'forced_login_method="chatgpt"' in invocation['argv']
        assert lab.base.read(target/'input.json') == payload
        response = lab.validate_response(lab.base.read(target/'final.json'), payload)
        for key, value in usage.items():
            total[key] = total.get(key, 0)+value
        passed.append(dict(jobId=name, responseValid=True,
                           nonliteralCitations=lab.citation_errors(response, payload)))
    assert total == summary['knownUsage']
    assert summary['statusCounts'] == {'completed': 28}
    assert not summary['unknownConsumption']
    assert summary['billing'] == 'chatgpt_subscription_limits'
    assert summary['actualApiChargeUSD'] is None
    assert summary['groups']['curatedReal']['scored'] == 3
    assert summary['groups']['curatedControls']['scored'] == 20
    assert summary['groups']['retrievedReal']['scored'] == 3
    result = dict(verifiedAt=lab.base.now(), realCompletedEvaluations=len(passed),
        curatedInputsIdenticalToFrozenV2=True, originalJevInputsVerified=True,
        rawResponseAndEventHashesVerified=True, reportedUsageReconciled=True,
        unexpectedToolItems=0, probabilitiesFabricated=False,
        evaluator='Luna through explicitly authorized subscription, experiment only',
        inferenceCallsDuringVerification=0, results=passed,
        summarySha256=lab.sha(directory/'summary.json'))
    lab.base.write(lab.ROOT/'reports/luna-subscription-verification.json', result)
    print(json.dumps({key: value for key, value in result.items() if key != 'results'}, ensure_ascii=False))


if __name__ == '__main__':
    main()

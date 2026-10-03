# Luna por suscripción: resultados del laboratorio

Modelo solicitado: gpt-5.6-luna; esfuerzo: xhigh; facturación: límites de suscripción.

| Grupo | Puntuados | Coincidencias | Falso apoyo | Falsa refutación | Propuestas tras controles | Errores retenidos |
|---|---:|---:|---:|---:|---:|---:|
| curatedReal | 0 | 0 | 0 | 0 | 0 | 0 |
| curatedControls | 0 | 0 | 0 | 0 | 0 | 0 |
| retrievedReal | 0 | 0 | 0 | 0 | 0 | 0 |

| Caso | Estado | Referencia | Luna | Control posterior |
|---|---|---|---|---|
| curated-R01 | failed_or_uncertain | supported | — | no_valid_response |
| curated-R02 | not_attempted | supported | — | no_valid_response |
| curated-R03 | not_attempted | exploratorio | — | no_valid_response |
| curated-R04 | not_attempted | insufficient | — | no_valid_response |
| curated-C01 | not_attempted | contradicted | — | no_valid_response |
| curated-C02 | not_attempted | contradicted | — | no_valid_response |
| curated-C03 | not_attempted | insufficient | — | missing_evidence |
| curated-C04 | not_attempted | insufficient | — | only_reported_statements |
| curated-C05 | not_attempted | insufficient | — | no_valid_response |
| curated-C06 | not_attempted | insufficient | — | no_valid_response |
| curated-C07 | not_attempted | supported | — | no_valid_response |
| curated-F01 | not_attempted | supported | — | no_valid_response |
| curated-F02 | not_attempted | supported | — | no_valid_response |
| curated-F03 | not_attempted | contradicted | — | no_valid_response |
| curated-F04 | not_attempted | insufficient | — | different_reference_period |
| curated-F05 | not_attempted | insufficient | — | no_valid_response |
| curated-F06 | not_attempted | not_verifiable | — | no_valid_response |
| curated-F07 | not_attempted | insufficient | — | only_reported_statements |
| curated-F08 | not_attempted | insufficient | — | no_valid_response |
| curated-F09 | not_attempted | supported | — | no_valid_response |
| curated-F10 | not_attempted | supported | — | no_valid_response |
| curated-F11 | not_attempted | contradicted | — | no_valid_response |
| curated-F12 | not_attempted | conflicting | — | no_valid_response |
| curated-F13 | not_attempted | supported | — | no_valid_response |
| retrieved-R01 | not_attempted | supported | — | no_valid_response |
| retrieved-R02 | not_attempted | supported | — | no_valid_response |
| retrieved-R03 | not_attempted | exploratorio | — | no_valid_response |
| retrieved-R04 | not_attempted | insufficient | — | no_valid_response |

## Consumo y tiempo

{
  "knownUsage": {},
  "unknownConsumption": [
    "curated-R01"
  ],
  "latency": {
    "curated": {
      "samples": 0,
      "p50Seconds": null,
      "p95Seconds": null,
      "totalSuccessfulSeconds": 0
    },
    "retrieved": {
      "samples": 0,
      "p50Seconds": null,
      "p95Seconds": null,
      "totalSuccessfulSeconds": 0
    }
  }
}

## Límites

- Reference authored by assistant, not independently human reviewed; R03 unscored.
- Small correlated sample from one session, not general production accuracy.
- CLI overhead and subscription usage are not TypeSafe/API cost or latency.
- No probability or confidence is requested or fabricated; Jev 0.85 threshold is not applied.
- Retrieval labels use the original reference as an exploratory end-to-end comparison; bundles differ.
- Luna answers questions jointly; Jev evaluates questions independently.
- Model selected explicitly through CLI; resolved backend snapshot not attested by exec events.

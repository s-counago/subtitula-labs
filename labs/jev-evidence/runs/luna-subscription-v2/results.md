# Luna por suscripción: resultados del laboratorio

Modelo solicitado: gpt-5.6-luna; esfuerzo: xhigh; facturación: límites de suscripción.

| Grupo | Puntuados | Coincidencias | Falso apoyo | Falsa refutación | Propuestas tras controles | Errores retenidos |
|---|---:|---:|---:|---:|---:|---:|
| curatedReal | 3 | 3 | 0 | 0 | 2 | 0 |
| curatedControls | 20 | 20 | 0 | 0 | 8 | 0 |
| retrievedReal | 3 | 2 | 0 | 0 | 1 | 0 |

| Caso | Estado | Referencia | Luna | Control posterior |
|---|---|---|---|---|
| curated-R01 | completed | supported | supported | passes_structural_gates_without_confidence |
| curated-R02 | completed | supported | supported | passes_structural_gates_without_confidence |
| curated-R03 | completed | exploratorio | insufficient | insufficient |
| curated-R04 | completed | insufficient | insufficient | insufficient |
| curated-C01 | completed | contradicted | contradicted | passes_structural_gates_without_confidence |
| curated-C02 | completed | contradicted | contradicted | passes_structural_gates_without_confidence |
| curated-C03 | completed | insufficient | insufficient | missing_evidence |
| curated-C04 | completed | insufficient | insufficient | only_reported_statements |
| curated-C05 | completed | insufficient | insufficient | insufficient |
| curated-C06 | completed | insufficient | insufficient | insufficient |
| curated-C07 | completed | supported | supported | passes_structural_gates_without_confidence |
| curated-F01 | completed | supported | supported | passes_structural_gates_without_confidence |
| curated-F02 | completed | supported | supported | passes_structural_gates_without_confidence |
| curated-F03 | completed | contradicted | contradicted | passes_structural_gates_without_confidence |
| curated-F04 | completed | insufficient | insufficient | different_reference_period |
| curated-F05 | completed | insufficient | insufficient | insufficient |
| curated-F06 | completed | not_verifiable | not_verifiable | not_verifiable |
| curated-F07 | completed | insufficient | insufficient | only_reported_statements |
| curated-F08 | completed | insufficient | insufficient | insufficient |
| curated-F09 | completed | supported | supported | passes_structural_gates_without_confidence |
| curated-F10 | completed | supported | supported | missing_or_nonliteral_citation |
| curated-F11 | completed | contradicted | contradicted | missing_or_nonliteral_citation |
| curated-F12 | completed | conflicting | conflicting | conflicting |
| curated-F13 | completed | supported | supported | passes_structural_gates_without_confidence |
| retrieved-R01 | completed | supported | supported | passes_structural_gates_without_confidence |
| retrieved-R02 | completed | supported | insufficient | insufficient |
| retrieved-R03 | completed | exploratorio | insufficient | insufficient |
| retrieved-R04 | completed | insufficient | insufficient | insufficient |

## Consumo y tiempo

{
  "knownUsage": {
    "input_tokens": 103479,
    "cached_input_tokens": 1792,
    "cache_write_input_tokens": 0,
    "output_tokens": 14072,
    "reasoning_output_tokens": 9602
  },
  "unknownConsumption": [],
  "latency": {
    "curated": {
      "samples": 24,
      "p50Seconds": 9.6267145,
      "p95Seconds": 21.465171,
      "totalSuccessfulSeconds": 281.147094
    },
    "retrieved": {
      "samples": 4,
      "p50Seconds": 16.831131,
      "p95Seconds": 40.231659,
      "totalSuccessfulSeconds": 87.407569
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

# M10: agentic layer, dev results (anecdotal)

Dev set, 30 questions (24 answerable, 6 unanswerable). One pass per config.
The gate threshold and the prompt were tuned on dev, so these numbers are optimistic.
Output varies slightly between runs at temperature 0 (not measured).

## Design
Graph: route -> retrieve -> grade -> (retry, weak band only) -> finish -> reply -> check.
- route: regex for whole-message greetings or thanks.
- grade: top-1 cross-encoder score. Strong >= 1.5, weak 0.0 to 1.5, hopeless < 0.0.
- retry: one LLM keyword query, trusted only if its top section is strong AND in the original question's hybrid top 5. The rule was proposed after seeing three failures and is not validated.
- check: code-only checks on the generated answer (empty, bad_citation, no_citation). It flags but does not repair.
- The agent does not use conversation history (no query rewriting), so follow-ups are not handled there.

## Naive vs agentic (dev)
| Metric | Naive | Agentic |
|---|---|---|
| Unanswerable refused | 5 of 6 | 5 of 6 |
| Answerable wrongly refused | 2 of 24 | 1 of 24 |
| Generated answers | 23 | 24 |
| no_citation / bad_citation | 2 / 0 | 2 / 0 |
| Latency p50 | 34.1 s | 36.7 s |
| Latency p95 (29th of 30) | 58.8 s | 57.1 s |

The only row that differs is dev-020: gate-refused in naive, answered in agentic after a trusted retry.
The retry ran on 3 rows (dev-016, dev-020, dev-029).
dev-016 and dev-029 stayed refused.
The net gain is 1 question of 24, based on a retry design fitted on 3 examples.
The p50 difference is within run-to-run variation.

## Limits
- dev-027 and dev-028 pass the gate (near-coverage questions); only the model can refuse them.
- The verify flags did not reduce no_citation.
- The test set has not been run yet.
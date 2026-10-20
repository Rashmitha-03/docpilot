# Test-set results (held out, one pass per config, config frozen before the run)

Test set: 18 questions (14 answerable, 4 unanswerable). Counts are descriptive; samples are tiny.

## Retrieval (hybrid, 14 answerable)
| Metric | Dev (24) | Test (14) |
|---|---|---|
| recall@1 | 0.743 | 0.607 |
| recall@3 | 0.917 | 0.714 |
| recall@5 | 0.979 | 0.750 |
| recall@10 | 0.979 | 0.893 |
| MRR | 0.927 | 0.736 |

Dev was used for tuning; test was not. Test recall is lower. Misses outside the top 5: test-001, test-002.

## Answers (naive vs agent)
| Metric | Naive | Agent |
|---|---|---|
| Unanswerable refused | 4 of 4 | 4 of 4 |
| Answerable wrongly refused | 1 of 14 (test-001) | 1 of 14 (test-001) |
| Generated | 13 | 13 |
| no_citation / bad_citation | 1 / 0 | 1 / 0 |

The retry never fired on test (no row in the weak band). The agent changed no outcome.
Gold in sources 12 of 14 and gold cited 11 of 14, identical in both configs (test-001 refused, test-002 wrong sources, test-006 not cited).
The gold-in-sources check was run on both the naive and the agent file.

## Notes
- Latency is not compared on test: test-008 took 254 s in the naive run (laptop slept), and the agent run was faster. Use the dev latency numbers.
- 6 of 18 answer texts differed between configs, so output varies between runs at temperature 0.
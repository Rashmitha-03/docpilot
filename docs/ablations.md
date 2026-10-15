# Retrieval ablations (dev set, v3 labels)

24 answerable dev questions. k = distinct sections (file, anchor).
Compare rows on v3 labels only. Test set not used.

| Config | recall@1 | recall@3 | recall@5 | recall@10 | MRR |
|---|---|---|---|---|---|
| Vector | 0.618 | 0.944 | 1.000 | 1.000 | 0.875 |
| BM25 | 0.639 | 0.833 | 0.896 | 0.979 | 0.832 |
| Hybrid (RRF, pool 30, k 60) | 0.743 | 0.917 | 0.979 | 0.979 | 0.927 |
| Hybrid + rerank (30 candidates) | 0.743 | 0.896 | 0.917 | 0.938 | 0.920 |
| Hybrid + rerank (10 candidates) | 0.743 | 0.896 | 0.896 | 0.979 | 0.924 |

## Latency (CPU, warm, k=5, 24 questions)

| Config | p50 | p95 |
|---|---|---|
| Hybrid | 65 ms | 107 ms |
| Hybrid + rerank (10) | 870 ms | 1057 ms |

## Notes
- recall is the fraction of a question's gold sections found; multi-gold
  questions can score partial recall (e.g. dev-008, second gold at rank 11).
- Rerank at 10 candidates: top 10 reranked, rest kept in hybrid order, so
  recall@10 mostly reflects hybrid depth.
- dev-005 drops under rerank (gold correct, cross-encoder favors async-heavy
  chunks). Hypothesis, not verified.
- Labels changed on dev only (dev-002, dev-021), based on evidence.
- All settings (RRF_K, POOL, CANDIDATES, chunk size) are untuned guesses.


# Answer-level results (dev, one pass, llama3.2:3b)

30 dev rows (24 answerable, 6 unanswerable). Pipeline: cross-encoder gate
(top-1 ce < 1.5 refuses), then hybrid top 5, then generation.
The gate threshold and the prompt's named-tool rule were chosen using dev
rows, so these numbers are optimistic. Test set not used.

| Measure | Result |
|---|---|
| Unanswerable refused | 5 of 6 (4 by gate, 1 by model) |
| Answerable wrongly refused | 2 of 24 (dev-016, dev-020, both by gate) |
| Answered answerable with no citation | 1 of 22 (dev-002) |
| Citations pointing outside the 5 sources | 0 of 22 |
| Answers citing at least one gold section | 20 of 22 (lenient: any cited section) |

## Latency (CPU, one pass)

| Path | Median |
|---|---|
| Gate refusal (no LLM call) | about 1.1 s |
| Generated answer | about 41 s |
| All 30 rows | p50 34.1 s, p95 58.6 s |

## Known failures and limits
- dev-028 (Sentry): the model says the context does not mention it, then
  answers anyway. Counted as answered.
- Cosine and RRF top-1 scores do not separate answerable from unanswerable
  questions; only the cross-encoder score partly does.
- dev-003: the answer stated `@app.get()` although no retrieved passage
  contained it, while its citation looked valid.
- Faithfulness was not reliably measured: a llama3.2:3b judge flagged 8 of 22
  answers, and 2 of the 3 flags checked by hand were false alarms.
- Output is not exactly repeatable between runs.
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
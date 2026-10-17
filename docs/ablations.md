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

## M9: Conversational follow-ups (query rewriting)

**Problem.** A context-free follow-up ("What about making it required?") was refused by the gate with no sources, because it has no topic words.

**Fix.** `generation/rewrite.py` rewrites the follow-up into a standalone question using the last 2 user questions, before retrieval. No history means no LLM call. `answer(question, history=None)` returns the rewritten text under `standalone`.

**Prompt iterations (3B model).**
1. Rules only: dropped "required" and copied the earlier question.
2. Added two examples: fixed that, but the old topic leaked into a standalone question.
3. Added a topic-change example and a "names its own topic" rule: both worked.

**Checks (hand-picked, not a measured eval).**
- Follow-up "What about making it required?": rewritten correctly, not refused, answer cites `query-params.md#required-query-parameters`.
- Topic change, first turn, pronoun and shorthand cases: sensible output.
- Chained follow-up (header, then cookies, then "delete it"): resolved to the older topic (headers). Known limit.

**Limits.** History must contain standalone versions of past questions for chains to resolve; to be handled where history is stored (API/UI, M11/M12). Rewrite adds about 2 s per follow-up turn (warm model). Rewrite accuracy is not measured on a labelled set.

**Generation latency (measured).** On a Ryzen 5 5500U (CPU only), llama3.2:3b reads prompts at about 34 to 43 tokens/s (about 19 s for a typical 800-token prompt; 1,332 tokens took 39 s cold) and writes at about 8 to 10 tokens/s. A fresh query therefore takes about 30 to 35 s warm, plus about 12 s if the model must reload. Not investigated: memory pressure. Accepted as a hardware limit; the live demo would use a hosted API to avoid it.

## M10 pre-check: where the gate fails (dev, 30 questions, untuned)

Top-1 cross-encoder score per question, gate at 1.5.

| Group | Top-1 scores |
|---|---|
| Unanswerable (6) | -3.716, -3.290, -0.494, 1.345 (dev-029), 1.799 (dev-028), 5.792 (dev-027) |
| Answerable, below gate (2) | 0.959 (dev-016), 1.046 (dev-020) |
| Answerable, above gate (22) | 1.762 to 8.932 |

- Both wrongly refused answerable questions are gate failures, not retrieval failures. dev-020: the gold section was top-1 but scored 1.046. dev-016: both gold sections were in the hybrid top 2, but the cross-encoder ranked a neighbouring non-gold section first (0.959).
- Grey zone 0.9 to 1.5 holds 2 answerable and 1 unanswerable question (dev-029, 1.345). Lowering the threshold would trade one wrong refusal for one wrong answer; not done.
- dev-027 (5.792) and dev-028 (1.799) are unanswerable but pass the gate. Only the model's own refusal can catch them.
- Both wrong refusals are first-turn questions, so M9 rewriting cannot help them.


# DocPilot

A citation-first Q&A assistant over the FastAPI documentation. It answers with references to the exact doc file and section, and refuses when the docs don't cover the question. Everything runs locally and for free (CPU only, Ollama).

> **Status: work in progress.** Retrieval, grounded generation, answer-level evaluation and follow-up handling are done. The agentic layer, API, UI, CI and a live demo are not built yet. Results below are on the **dev set only**; the held-out test set has not been run.

## How it works

```
FastAPI docs (Markdown)
  -> section-aware chunker (180 words, 30 overlap, header path in chunk text)
  -> embeddings (bge-small-en-v1.5) + BM25 index
  -> hybrid retrieval (Reciprocal Rank Fusion, pool 30, k=5)
  -> cross-encoder score (ms-marco-MiniLM-L-6-v2) used as a refusal gate
  -> grounded generation (llama3.2:3b via Ollama) with [n] citations
```

Follow-up questions ("What about making it required?") are first rewritten into standalone questions using the previous user questions.

## Corpus

FastAPI docs, commit `f5c6e9b`: 155 files, 1,372 chunks. See `data/manifest.md`.

## Results (DEV set, 30 questions; hand-written labels)

Retrieval, with k counted in distinct sections:

| Config | recall@1 | recall@3 | recall@5 | recall@10 | MRR |
|---|---|---|---|---|---|
| Vector | 0.618 | 0.944 | 1.000 | 1.000 | 0.875 |
| BM25 | 0.639 | 0.833 | 0.896 | 0.979 | 0.832 |
| **Hybrid (used)** | **0.743** | 0.917 | 0.979 | 0.979 | **0.927** |
| Hybrid + rerank (30) | 0.743 | 0.896 | 0.917 | 0.938 | 0.920 |
| Hybrid + rerank (10) | 0.743 | 0.896 | 0.896 | 0.979 | 0.924 |

Latency: hybrid p50 65 ms / p95 107 ms; rerank (10 candidates) p50 870 ms / p95 1057 ms.

Reranking did not improve ranking on this corpus, so the cross-encoder is used only as a refusal gate (top-1 score below 1.5 means "not in the docs").

Answer level (30 dev questions, one pass):

| Measure | Result |
|---|---|
| Unanswerable questions refused | 5 of 6 |
| Answerable questions wrongly refused | 2 of 24 |
| Answers with no citation | 1 of 22 |
| Citations outside the retrieved sources | 0 of 22 |
| Answers citing at least one gold section | 20 of 22 (lenient) |
| Latency | p50 34.1 s, p95 58.6 s (gate refusal about 1.1 s) |

**Caveat:** the refusal threshold and prompt rules were tuned by eye on the dev set, so these answer-level numbers are optimistic. The test set is held out and will be run once, at the end.

## Design decisions

- **Eval set before system.** Labels were written first, with a dev/test split, so tuning cannot leak into reported results.
- **Hybrid over vector-only.** BM25 catches exact identifiers the embeddings miss. Measured gain at recall@1 and MRR; small eval set, so differences of a few rows are not conclusive.
- **Cross-encoder as a gate, not a ranker.** Measured: it did not help ranking, but its top score separates answerable from unanswerable questions better than cosine or RRF scores.
- **Query rewriting for follow-ups.** Without it, a follow-up with no topic words is refused by the gate. Rewriting adds about 2 s per follow-up turn.
- **LLM-as-judge dropped.** The 3B judge was too noisy to trust (see `docs/ablations.md`).

## Limitations

- Generation takes about 41 s per answer on CPU; cause not yet investigated.
- The 3B model sometimes answers from outside the retrieved passages or produces invalid code; formatting slips ("declaringthe", glued citations).
- The refusal threshold is untuned; near-coverage questions can be wrongly refused or wrongly answered.
- Rewrite quality is checked on a few hand-picked cases, not a labelled set. Chained follow-ups can resolve to the older topic.
- Output varies slightly between runs even at temperature 0; this variation is not measured.
- Small eval set: treat small metric differences as noise.

## Run it

Requires Python 3.12 and [Ollama](https://ollama.com) with `llama3.2:3b` pulled.

```powershell
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Clone the FastAPI docs into `data/fastapi_repo/`, build the index, then run from the repo root:

```powershell
python -m eval.run_eval hybrid
python -m eval.run_answers
```

(Exact index-build and demo commands will be added once the API and UI exist.)

## Project layout

```
docpilot/   ingest/, retrieval/, generation/   (package)
eval/       dev.jsonl, test.jsonl, metrics.py, run_eval.py, run_answers.py, results/
docs/       ablations.md (full tables, failures, iterations)
tests/      test_metrics.py
data/       manifest.md
```

## Roadmap

Agentic layer (router, grader, retry cap), FastAPI service with streaming, Streamlit UI, tests and CI, live demo, final test-set run.
# DocPilot

A citation-first Q&A assistant over the FastAPI documentation. It answers with references to the exact doc file and section, and refuses when the docs don't cover the question. Everything runs locally and for free (CPU only, Ollama).

> **Status: work in progress.** Retrieval, grounded generation, answer-level evaluation and follow-up handling are done. The agentic layer is built and evaluated on dev (small, anecdotal effect: 1 question of 24). The API, UI, CI and a live demo are not built yet. Dev results below are optimistic (tuned on dev); the held-out test set was run once (see "Test results")..

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

**Caveat:** the refusal threshold and prompt rules were tuned by eye on the dev set, so these answer-level numbers are optimistic. The test set was held out and run once; see "Test results".

## Design decisions

- **Eval set before system.** Labels were written first, with a dev/test split, so tuning cannot leak into reported results.
- **Hybrid over vector-only.** BM25 catches exact identifiers the embeddings miss. Measured gain at recall@1 and MRR; small eval set, so differences of a few rows are not conclusive.
- **Cross-encoder as a gate, not a ranker.** Measured: it did not help ranking, but its top-1 score works as a refusal gate (threshold 1.5, chosen by eye on dev). On dev it catches 4 of 6 unanswerable questions; scores overlap, so it cannot catch topic-matching ones. I did not compare it against cosine or RRF scores as a gate.
- **Query rewriting for follow-ups.** Without it, a follow-up with no topic words is refused by the gate. Rewriting adds about 2 s per follow-up turn.
- **LLM-as-judge dropped.** The 3B judge was too noisy to trust (see `docs/ablations.md`).

## Limitations

- Generation takes about 35 s per answer on CPU (p50 on dev). Measured: prompt reading is about 34 to 43 tokens/s and writing about 8 to 10 tokens/s, plus about 12 s model load; accepted as a CPU limitation.
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
## Design decisions
- **Agentic layer: small effect.** Router, grader, one retry and a code-only answer check were added. On dev it changed 1 of 30 outcomes (dev-020, rescued by the retry); the retry rule was fitted on 3 examples, so this is anecdotal. See `docs/ablations_m10.md`.

## Test results

Held-out test set, one pass, config frozen beforehand: 14 answerable and 4 unanswerable questions. Counts are descriptive only.
- Retrieval (hybrid): recall@1 0.607, recall@5 0.750, recall@10 0.893, MRR 0.736 (dev: 0.743, 0.979, 0.979, 0.927). Dev was tuned on, so it overstates.
- Refusal: 4 of 4 unanswerable refused; 1 of 14 answerable wrongly refused (test-001, whose gold section ranked about 19th).
- Citations: 0 outside the sources; gold section cited in 11 of 14 answers.

## Roadmap

FastAPI service with streaming, Streamlit UI, tests and CI, live demo, final test-set run.

## API

Run from the repo root (venv active):

    python -m uvicorn docpilot.api.main:app --port 8000

- `GET /health` returns `{"status": "ok"}`.
- `POST /ask` takes `{"question", "mode", "history"}` and returns the full answer. `mode` is `naive` (default) or `agent`. `history` is used only by the naive path.
- `POST /ask/stream` streams the naive path as Server-Sent Events: one `meta` event (sources, standalone question), then `token` events, then `done`.

API limitations:
- On the stream, `meta` is sent before generation, so a refusal by the model arrives with `refused_by: null`. Clients can detect it by comparing the text to the refusal sentence. `/ask` sets `refused_by: "model"` correctly.
- Models load on the first request, so the first call is slow (about 12 s for model load, then about 35 s per answer on CPU).

## UI

Streamlit chat app. It calls the API, so start the server first (see API), then in a second window:

    python -m streamlit run app\streamlit_app.py

- Answers stream token by token, with a collapsible Sources panel (file and section) under each answer.
- Follow-up questions are rewritten into standalone questions using the chat history.
- A Debug panel shows the rewritten question and whether the gate, the model, or neither refused.

UI limitations:
- Naive path only (the agent is not streamed).
- The Debug panel infers model refusals by comparing the text to the refusal sentence.
- Follow-up rewriting is only lightly checked (a few hand-picked cases).
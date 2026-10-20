import json

import ollama

from docpilot.generation.answer import CE_THRESHOLD, MODEL
from docpilot.generation.prompts import REFUSAL, build_messages
from docpilot.generation.rewrite import rewrite_question
from docpilot.retrieval import hybrid, rerank


def _sse(event, data):
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def stream_answer(question, history=None, k=5, threshold=CE_THRESHOLD):
    """Naive path as a generator of SSE strings. Same steps as answer()."""
    question = rewrite_question(history or [], question)
    top = rerank.search(question, k=1)
    if not top or top[0].score < threshold:
        yield _sse("meta", {"refused_by": "gate", "sources": [], "standalone": question})
        yield _sse("token", REFUSAL)
        yield _sse("done", {})
        return
    hits = hybrid.search(question, k=k)
    msgs, sources = build_messages(question, hits)
    yield _sse("meta", {"refused_by": None, "sources": sources, "standalone": question})
    for part in ollama.chat(model=MODEL, messages=msgs, stream=True,
                            options={"temperature": 0}):
        piece = part["message"]["content"]
        if piece:
            yield _sse("token", piece)
    yield _sse("done", {})
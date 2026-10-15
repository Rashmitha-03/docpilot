"""Retrieve, gate on the cross-encoder score, then generate."""
import ollama

from docpilot.generation.prompts import REFUSAL, build_messages
from docpilot.generation.rewrite import rewrite_question
from docpilot.retrieval import hybrid, rerank

MODEL = "llama3.2:3b"
CE_THRESHOLD = 1.5  # chosen by eye from dev scores, untuned


def answer(question, k=5, threshold=CE_THRESHOLD, history=None):
    original = question
    question = rewrite_question(history or [], question)
    top = rerank.search(question, k=1)
    if not top or top[0].score < threshold:
        return {"answer": REFUSAL, "refused_by": "gate", "sources": [], "standalone": question}
    hits = hybrid.search(question, k=k)
    msgs, sources = build_messages(question, hits)
    resp = ollama.chat(model=MODEL, messages=msgs, options={"temperature": 0})
    out = resp["message"]["content"].strip()
    by = "model" if out == REFUSAL else None
    return {"answer": out, "refused_by": by, "sources": sources, "standalone": question}
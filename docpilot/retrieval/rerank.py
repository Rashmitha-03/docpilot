"""Cross-encoder rerank of the hybrid candidates."""
from dataclasses import replace

from sentence_transformers import CrossEncoder

from docpilot.retrieval import hybrid

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
CANDIDATES = 10  # how many hybrid chunks get reranked (untuned)

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = CrossEncoder(MODEL_NAME)
    return _model


def search(query, k=5):
    allc = hybrid.search(query, k=max(k, CANDIDATES))
    if not allc:
        return []
    head, tail = allc[:CANDIDATES], allc[CANDIDATES:]
    scores = _get_model().predict([(query, h.text) for h in head])
    ranked = sorted(zip(head, scores), key=lambda p: p[1], reverse=True)
    out = [replace(h, score=float(s)) for h, s in ranked] + tail
    return out[:k]
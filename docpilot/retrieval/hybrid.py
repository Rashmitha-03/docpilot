from docpilot.config import settings
from docpilot.retrieval import bm25, vector

RRF_K = 60
POOL = 30


def search(query: str, k: int | None = None):
    k = k or settings.top_k
    fused: dict[str, float] = {}
    hits_by_id = {}
    for retriever in (vector, bm25):
        for rank, h in enumerate(retriever.search(query, k=POOL), start=1):
            fused[h.id] = fused.get(h.id, 0.0) + 1.0 / (RRF_K + rank)
            hits_by_id.setdefault(h.id, h)
    order = sorted(fused, key=fused.get, reverse=True)[:k]
    return [
        type(hits_by_id[i])(**{**hits_by_id[i].__dict__, "score": fused[i]})
        for i in order
    ]
import re
from functools import lru_cache

import chromadb
from rank_bm25 import BM25Okapi

from docpilot.config import settings
from docpilot.ingest.indexer import COLLECTION
from docpilot.retrieval.vector import Hit

_TOKEN = re.compile(r"[a-z0-9_]+")


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


@lru_cache(maxsize=1)
def _index():
    client = chromadb.PersistentClient(path=str(settings.chroma_dir))
    col = client.get_collection(COLLECTION)
    data = col.get(include=["documents", "metadatas"])
    ids, docs, metas = data["ids"], data["documents"], data["metadatas"]
    bm25 = BM25Okapi([tokenize(d) for d in docs])
    return bm25, ids, docs, metas


def search(query: str, k: int | None = None) -> list[Hit]:
    k = k or settings.top_k
    bm25, ids, docs, metas = _index()
    scores = bm25.get_scores(tokenize(query))
    order = sorted(range(len(ids)), key=lambda i: scores[i], reverse=True)[:k]
    return [
        Hit(
            id=ids[i],
            file=metas[i]["file"],
            anchor=metas[i]["anchor"],
            header=metas[i]["header"],
            text=docs[i],
            score=float(scores[i]),
        )
        for i in order
    ]
from dataclasses import dataclass
from functools import lru_cache

import chromadb
from sentence_transformers import SentenceTransformer

from docpilot.config import settings
from docpilot.ingest.indexer import COLLECTION

# BGE: this prefix goes on QUERIES only, never on stored chunks.
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


@dataclass
class Hit:
    id: str
    file: str
    anchor: str
    header: str
    text: str
    score: float  # cosine similarity = 1 - cosine distance


@lru_cache(maxsize=1) #Loads the model and opens Chroma once per process, not per query
def _model() -> SentenceTransformer:
    return SentenceTransformer(settings.embed_model)


@lru_cache(maxsize=1)
def _collection():
    client = chromadb.PersistentClient(path=str(settings.chroma_dir))
    return client.get_collection(COLLECTION)


def search(query: str, k: int | None = None) -> list[Hit]:
    k = k or settings.top_k
    vec = _model().encode(QUERY_PREFIX + query, normalize_embeddings=True)
    res = _collection().query(
        query_embeddings=[vec.tolist()],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    hits = []
    for id_, doc, meta, dist in zip(
        res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        hits.append(Hit(id_, meta["file"], meta["anchor"], meta["header"], doc, 1 - dist))
    return hits
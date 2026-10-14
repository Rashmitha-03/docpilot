import time

import chromadb
from sentence_transformers import SentenceTransformer

from docpilot.config import settings
from docpilot.ingest.chunker import chunk_doc
from docpilot.ingest.loader import load_docs

COLLECTION = "docpilot"
BATCH = 32


def build_index() -> int:
    chunks = []
    for d in load_docs():
        chunks.extend(chunk_doc(d))

    model = SentenceTransformer(settings.embed_model)
    client = chromadb.PersistentClient(path=str(settings.chroma_dir))
    try:
        client.delete_collection(COLLECTION)  # rebuild from scratch each run
    except Exception:
        pass
    col = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})

    start = time.time()
    for i in range(0, len(chunks), BATCH):
        batch = chunks[i : i + BATCH]
        embeddings = model.encode(
            [c.text for c in batch], normalize_embeddings=True
        ).tolist()
        col.upsert(
            ids=[c.id for c in batch],
            embeddings=embeddings,
            documents=[c.text for c in batch],
            metadatas=[
                {"file": c.file, "anchor": c.anchor or "", "header": c.header}
                for c in batch
            ],
        )
        if (i // BATCH) % 10 == 0:
            print(f"{i + len(batch)}/{len(chunks)}", flush=True)
    print("seconds:", round(time.time() - start, 1))
    return col.count()


if __name__ == "__main__":
    print("chunks in Chroma:", build_index())
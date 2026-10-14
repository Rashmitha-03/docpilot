import json
from pathlib import Path

from sentence_transformers import SentenceTransformer

from docpilot.ingest.chunker import chunk_doc
from docpilot.ingest.loader import load_docs

chunks = []
for d in load_docs():
    chunks.extend(chunk_doc(d))

# 1) gold labels vs chunks
have = {(c.file, c.anchor) for c in chunks}
checked = missing = 0
for name in ["eval/dev.jsonl", "eval/test.jsonl"]:
    for line in Path(name).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        for g in row.get("gold", []):
            checked += 1
            if (g["file"], g["anchor"]) not in have:
                missing += 1
                print("NOCHUNK:", row["id"], g["file"], g["anchor"])
print("gold labels checked:", checked)
print("gold labels with no chunk:", missing)

# 2) token lengths of the real chunk text
tok = SentenceTransformer("BAAI/bge-small-en-v1.5").tokenizer
pairs = [(len(tok.encode(c.text, add_special_tokens=True)), c) for c in chunks]
lens = sorted(t for t, _ in pairs)
n = len(lens)
for t, c in sorted(pairs, key=lambda p: -p[0]):
    if t > 512:
        print("BIG:", t, "tok |", len(c.text.split()), "words |", c.id)
print("median tokens:", lens[n // 2])
print("p99 tokens:", lens[int(n * 0.99)])
print("max tokens:", lens[-1])
print("over 512 tokens:", sum(1 for t in lens if t > 512))
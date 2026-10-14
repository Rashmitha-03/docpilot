import os

from docpilot.retrieval import rerank
from eval.run_eval import DEV, load_rows

row = next(r for r in load_rows(DEV) if r["id"] == os.environ["QID"])
print("Q:", row["question"])
hits = rerank.search(row["question"], k=3)
for h in hits:
    print(f"ce={h.score:.2f}", h.file, h.anchor or "(no anchor)")
print("--- top passage ---")
print(hits[0].text[:600])
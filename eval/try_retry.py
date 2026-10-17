import json
import time

from docpilot.agent.nodes import grade, retry_query
from docpilot.retrieval import rerank

with open("eval/dev.jsonl", encoding="utf-8") as f:
    rows = [json.loads(line) for line in f if line.strip()]

for r in rows:
    q = r["question"]
    top = rerank.search(q, k=1)[0]
    if grade(top.score) != "weak":
        continue
    t = time.time()
    q2 = retry_query(q)
    new = rerank.search(q2, k=1)[0]
    secs = time.time() - t
    print("=" * 70)
    print(r["id"], "answerable =", r["answerable"])
    print("gold:", [g["anchor"] for g in (r.get("gold") or [])])
    print("original query :", q)
    print(f"  before: {top.score:.3f} {grade(top.score)}  {top.anchor}")
    print("retry query    :", q2)
    print(f"  after : {new.score:.3f} {grade(new.score)}  {new.anchor}")
    print(f"retry cost: {secs:.1f} s")
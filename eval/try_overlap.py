import json

from docpilot.agent.nodes import grade, retry_query
from docpilot.retrieval import hybrid, rerank

with open("eval/dev.jsonl", encoding="utf-8") as f:
    rows = [json.loads(line) for line in f if line.strip()]

for r in rows:
    q = r["question"]
    if grade(rerank.search(q, k=1)[0].score) != "weak":
        continue
    orig = {(h.file, h.anchor) for h in hybrid.search(q, k=5)}
    new = rerank.search(retry_query(q), k=1)[0]
    print(r["id"], "retry top:", new.anchor,
          "| in original hybrid top 5:", (new.file, new.anchor) in orig)
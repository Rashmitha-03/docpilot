import json

from docpilot.agent.nodes import grade
from docpilot.retrieval import rerank

with open("eval/dev.jsonl", encoding="utf-8") as f:
    rows = [json.loads(line) for line in f if line.strip()]

counts = {}
for r in rows:
    score = rerank.search(r["question"], k=1)[0].score
    g = grade(score)
    counts[(g, r["answerable"])] = counts.get((g, r["answerable"]), 0) + 1
    print(f"{score:7.3f}  {g:9}  {r['id']}  answerable={r['answerable']}")

print()
for (g, ans), n in sorted(counts.items()):
    print(f"{g:9} answerable={ans!s:5} -> {n}")
import json

from docpilot.agent.graph import graph

with open("eval/dev.jsonl", encoding="utf-8") as f:
    rows = [json.loads(line) for line in f if line.strip()]

counts = {}
for r in rows:
    out = graph.invoke({"question": r["question"]})
    key = (out["decision"], r["answerable"])
    counts[key] = counts.get(key, 0) + 1
    print(f"{r['id']}  answerable={r['answerable']!s:5}  decision={out['decision']:7}"
          f"  band={out['band']:9}  retried={out['retried']!s:5}"
          f"  trusted={out['retry_trusted']!s:5}  score={out['score']:.3f}")

print()
for (d, ans), n in sorted(counts.items()):
    print(f"{d:7} answerable={ans!s:5} -> {n}")
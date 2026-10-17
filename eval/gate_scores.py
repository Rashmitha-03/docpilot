import json

from docpilot.retrieval import rerank

rows = []
with open("eval/dev.jsonl", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            rows.append(json.loads(line))

print("dev rows:", len(rows))

out = []
for r in rows:
    h = rerank.search(r["question"], k=1)[0]
    gold = {(g["file"], g["anchor"]) for g in (r.get("gold") or [])}
    hit_gold = (h.file, h.anchor) in gold
    out.append((h.score, r["id"], r["answerable"], hit_gold, h.anchor))

out.sort()
for score, qid, ans, hit_gold, anchor in out:
    print(f"{score:7.3f}  {qid}  answerable={ans!s:5}  top1_is_gold={hit_gold!s:5}  {anchor}")
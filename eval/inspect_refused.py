import dataclasses
import json

from docpilot.retrieval import rerank

IDS = ["dev-016", "dev-020"]


def fields(h):
    if dataclasses.is_dataclass(h):
        d = dataclasses.asdict(h)
    elif hasattr(h, "_asdict"):
        d = h._asdict()
    else:
        d = dict(vars(h))
    d.pop("text", None)
    d.pop("header", None)
    d.pop("id", None)
    return {k: (round(v, 3) if isinstance(v, float) else v) for k, v in d.items()}


rows = {}
with open("eval/dev.jsonl", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            r = json.loads(line)
            rows[r["id"]] = r

for qid in IDS:
    q = rows[qid]["question"]
    print("=" * 70)
    print(qid, "| gold:", [g["anchor"] for g in rows[qid]["gold"]])
    for i, h in enumerate(rerank.search(q, k=10), 1):
        print(f"  {i}.", fields(h))
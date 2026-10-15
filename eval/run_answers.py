import json
import statistics
import time

from docpilot.generation.answer import answer
from docpilot.generation.prompts import REFUSAL
from eval.run_eval import DEV, load_rows

rows = load_rows(DEV)
answer(rows[0]["question"])  # warm-up: loads the models, excluded from the saved data

out, lat = [], []
for r in rows:
    t = time.perf_counter()
    res = answer(r["question"])
    ms = round((time.perf_counter() - t) * 1000)
    lat.append(ms)
    refused = res["answer"] == REFUSAL
    out.append({
        "id": r["id"],
        "question": r["question"],
        "answerable": r["answerable"],
        "gold": r["gold"],
        "answer": res["answer"],
        "refused": refused,
        "refused_by": res["refused_by"],
        "sources": res["sources"],
        "latency_ms": ms,
    })
    tag = "ANS" if r["answerable"] else "NO "
    print(tag, r["id"], "REFUSED" if refused else "answered", res["refused_by"], ms, "ms")

with open("eval/results/answers_dev.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

ans = [o for o in out if o["answerable"]]
no = [o for o in out if not o["answerable"]]
print("answerable refused:", sum(o["refused"] for o in ans), "of", len(ans))
print("unanswerable refused:", sum(o["refused"] for o in no), "of", len(no))
print("refused by gate:", sum(o["refused_by"] == "gate" for o in out),
      "| by model:", sum(o["refused_by"] == "model" for o in out))
print("latency p50 ms:", round(statistics.median(lat)))
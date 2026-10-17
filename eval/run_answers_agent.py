import json
import statistics
import time

from docpilot.agent.graph import graph
from docpilot.generation.prompts import REFUSAL
from eval.run_eval import DEV, load_rows

rows = load_rows(DEV)
graph.invoke({"question": rows[0]["question"]})  # warm-up: loads the models, excluded

out, lat = [], []
for r in rows:
    t = time.perf_counter()
    res = graph.invoke({"question": r["question"]})
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
        "refused_by": res["refused_by"] or None,
        "sources": res["sources"],
        "latency_ms": ms,
        "decision": res["decision"],
        "retried": res.get("retried"),
        "trusted": res.get("retry_trusted"),
        "verify": res["verify"],
    })
    tag = "ANS" if r["answerable"] else "NO "
    print(tag, r["id"], "REFUSED" if refused else "answered", res["refused_by"] or None,
          "retried" if res.get("retried") else "", res["verify"], ms, "ms", flush=True)

with open("eval/results/answers_dev_agent.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

ans = [o for o in out if o["answerable"]]
no = [o for o in out if not o["answerable"]]
print("answerable refused:", sum(o["refused"] for o in ans), "of", len(ans))
print("unanswerable refused:", sum(o["refused"] for o in no), "of", len(no))
print("refused by gate:", sum(o["refused_by"] == "gate" for o in out),
      "| by model:", sum(o["refused_by"] == "model" for o in out))
print("latency p50 ms:", round(statistics.median(lat)))
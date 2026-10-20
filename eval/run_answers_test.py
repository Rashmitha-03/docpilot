import json
import os
import statistics
import time
from pathlib import Path

from docpilot.generation.prompts import REFUSAL
from eval.run_eval import load_rows

CONFIG = os.environ.get("CONFIG")
if CONFIG not in ("naive", "agent"):
    raise SystemExit("Set $env:CONFIG to naive or agent")

rows = load_rows(Path("eval/test.jsonl"))
print("rows loaded:", len(rows), flush=True)

if CONFIG == "naive":
    from docpilot.generation.answer import answer

    def run(q):
        res = answer(q)
        return res, {}
else:
    from docpilot.agent.graph import graph

    def run(q):
        res = graph.invoke({"question": q})
        extra = {"decision": res["decision"], "retried": res.get("retried"),
                 "trusted": res.get("retry_trusted"), "verify": res["verify"]}
        res["refused_by"] = res["refused_by"] or None
        return res, extra

run("How do I declare a path parameter?")  # warm-up, not in dev or test

out, lat = [], []
for r in rows:
    t = time.perf_counter()
    res, extra = run(r["question"])
    ms = round((time.perf_counter() - t) * 1000)
    lat.append(ms)
    refused = res["answer"] == REFUSAL
    out.append({"id": r["id"], "question": r["question"], "answerable": r["answerable"],
                "gold": r["gold"], "answer": res["answer"], "refused": refused,
                "refused_by": res["refused_by"], "sources": res["sources"],
                "latency_ms": ms, **extra})
    print("ANS" if r["answerable"] else "NO ", r["id"],
          "REFUSED" if refused else "answered", res["refused_by"], ms, "ms", flush=True)

with open(f"eval/results/answers_test_{CONFIG}.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

ans = [o for o in out if o["answerable"]]
no = [o for o in out if not o["answerable"]]
print("answerable refused:", sum(o["refused"] for o in ans), "of", len(ans))
print("unanswerable refused:", sum(o["refused"] for o in no), "of", len(no))
print("latency p50 ms:", round(statistics.median(lat)))
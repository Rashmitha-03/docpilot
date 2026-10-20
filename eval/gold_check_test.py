import json
import re
import sys

CITE = re.compile(r"\[(\d+)\]")
path = sys.argv[1] if len(sys.argv) > 1 else "eval/results/answers_test_agent.json"

with open(path, encoding="utf-8") as f:
    rows = json.load(f)

n_ans = in_src = cited_gold = 0
for r in rows:
    if not r["answerable"]:
        continue
    n_ans += 1
    gold = {(g["file"], g["anchor"]) for g in r["gold"]}
    srcs = {s["n"]: (s["file"], s["anchor"]) for s in r["sources"]}
    has = bool(gold & set(srcs.values()))
    cited = {int(n) for n in CITE.findall(r["answer"])}
    cg = any(srcs.get(n) in gold for n in cited)
    in_src += has
    cited_gold += cg
    print(r["id"], "refused" if r["refused"] else "answered",
          "| gold in sources:", has, "| gold cited:", cg)

print("answerable:", n_ans, "| gold in sources:", in_src, "| gold cited:", cited_gold)
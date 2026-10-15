import json
import re

d = json.load(open("eval/results/answers_dev.json", encoding="utf-8"))
rows = [o for o in d if o["answerable"] and not o["refused"]]
no_cite = bad_range = gold_hit = 0
for o in rows:
    nums = [int(n) for n in re.findall(r"\[(\d+)\]", o["answer"])]
    gold = {(g["file"], g["anchor"]) for g in o["gold"]}
    srcs = {s["n"]: (s["file"], s["anchor"]) for s in o["sources"]}
    out_of_range = [n for n in nums if n not in srcs]
    hit = any(srcs.get(n) in gold for n in nums)
    no_cite += not nums
    bad_range += bool(out_of_range)
    gold_hit += hit
    print(o["id"], "cited:", sorted(set(nums)), "bad:", out_of_range, "gold:", hit)
print("answered answerable:", len(rows))
print("no citation:", no_cite, "| out-of-range:", bad_range, "| cites a gold section:", gold_hit)
import json
import os
import re

from docpilot.retrieval import hybrid

d = {x["id"]: x for x in json.load(open("eval/results/answers_dev.json", encoding="utf-8"))}
for qid in os.environ["QIDS"].split(","):
    o = d[qid]
    print("=====", qid, "Q:", o["question"])
    print("ANSWER:", o["answer"][:600])
    nums = sorted({int(n) for n in re.findall(r"\[(\d+)\]", o["answer"])}) or [1]
    hits = hybrid.search(o["question"], k=5)
    for n in nums[:2]:
        h = hits[n - 1]
        print(f"--- [{n}] {h.file}#{h.anchor}")
        print(h.text[:450])
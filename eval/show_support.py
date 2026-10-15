import json
import os
import re

from docpilot.retrieval import hybrid

d = json.load(open("eval/results/answers_dev.json", encoding="utf-8"))
o = next(x for x in d if x["id"] == os.environ["QID"])
print("Q:", o["question"])
print("ANSWER:", o["answer"])
nums = sorted({int(n) for n in re.findall(r"\[(\d+)\]", o["answer"])}) or [1]
hits = hybrid.search(o["question"], k=5)
for n in nums:
    h = hits[n - 1]
    print(f"--- passage [{n}] {h.file}#{h.anchor} ---")
    print(h.text[:700])
import json
import os

from docpilot.retrieval import hybrid

d = {x["id"]: x for x in json.load(open("eval/results/answers_dev.json", encoding="utf-8"))}
o = d[os.environ["QID"]]
hits = hybrid.search(o["question"], k=5)
print("Q:", o["question"])
for kw in os.environ["KW"].split(","):
    found = [(n, h.text) for n, h in enumerate(hits, 1) if kw.lower() in h.text.lower()]
    if not found:
        print(f"'{kw}': in NO passage")
    for n, t in found:
        i = t.lower().find(kw.lower())
        print(f"'{kw}': passage [{n}] ...{t[max(0, i - 50):i + 70]}...".replace("\n", " "))
import sys

from docpilot.retrieval import hybrid, rerank
from eval.run_eval import DEV, OVERFETCH, load_rows, unique_sections
import os
qid = os.environ["QID"]

row = next(r for r in load_rows(DEV) if r["id"] == qid)
print("Q:", row["question"])
print("GOLD:", [(g["file"], g["anchor"]) for g in row["gold"]])
for name, mod in (("hybrid", hybrid), ("rerank", rerank)):
    secs = unique_sections(mod.search(row["question"], k=OVERFETCH))
    print(name, "top 5:")
    for s in list(secs)[:5]:
        print("  ", s)
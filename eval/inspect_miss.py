import sys

from docpilot.retrieval.vector import search
from eval.run_eval import DEV, load_rows, unique_sections

row = next(r for r in load_rows(DEV) if r["id"] == sys.argv[1])
gold = {(g["file"], g["anchor"]) for g in row["gold"]}
print("Q:", row["question"])
for i, (f, a) in enumerate(unique_sections(search(row["question"], k=30))[:6], 1):
    print(i, "GOLD" if (f, a) in gold else "    ", f, "#" + (a or "-"))
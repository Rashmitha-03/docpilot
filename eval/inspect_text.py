import sys

from docpilot.retrieval.vector import search
from eval.run_eval import DEV, load_rows

row = next(r for r in load_rows(DEV) if r["id"] == sys.argv[1])
gold = {(g["file"], g["anchor"]) for g in row["gold"]}
print("Q:", row["question"])
seen = set()
shown = 0
for h in search(row["question"], k=30):
    key = (h.file, h.anchor)
    if key in seen:
        continue
    seen.add(key)
    shown += 1
    if shown > 5:
        break
    body = h.text.replace("\n", " ")[:260]
    print(shown, "GOLD" if key in gold else "    ", h.file, "#" + (h.anchor or "-"))
    print("   ", body)
from docpilot.retrieval.hybrid import search
from eval.run_eval import DEV, OVERFETCH, load_rows, unique_sections

for r in load_rows(DEV):
    if not r["answerable"]:
        continue
    gold = {(g["file"], g["anchor"]) for g in r["gold"]}
    secs = unique_sections(search(r["question"], k=OVERFETCH))
    ranks = [i for i, s in enumerate(secs, 1) if s in gold]
    if len(secs) < 10 or not ranks or ranks[0] > 10:
        print(r["id"], "sections:", len(secs), "gold rank:", ranks[:1] or "none")
        
print("--- multi-gold ---")
for r in load_rows(DEV):
    if not r["answerable"] or len(r["gold"]) < 2:
        continue
    gold = [(g["file"], g["anchor"]) for g in r["gold"]]
    secs = list(unique_sections(search(r["question"], k=OVERFETCH)))
    ranks = [secs.index(g) + 1 if g in secs else None for g in gold]
    print(r["id"], "gold:", len(gold), "ranks:", ranks, "sections:", len(secs))
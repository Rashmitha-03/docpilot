from docpilot.retrieval import hybrid, rerank, vector
from eval.run_eval import DEV, load_rows

rows = sorted(load_rows(DEV), key=lambda r: r["answerable"])
for r in rows:
    q = r["question"]
    v = vector.search(q, k=1)[0].score
    h = hybrid.search(q, k=1)[0].score
    c = rerank.search(q, k=1)[0].score
    tag = "ANS" if r["answerable"] else "NO "
    print(tag, r["id"], f"vec={v:.3f} rrf={h:.4f} ce={c:.2f}")
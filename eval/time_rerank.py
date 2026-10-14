import statistics
import time

from docpilot.retrieval import hybrid, rerank
from eval.run_eval import DEV, load_rows

qs = [r["question"] for r in load_rows(DEV) if r["answerable"]]
for name, mod in (("hybrid", hybrid), ("rerank", rerank)):
    mod.search(qs[0], k=5)  # warm-up, excluded from timing
    ts = []
    for q in qs:
        t = time.perf_counter()
        mod.search(q, k=5)
        ts.append((time.perf_counter() - t) * 1000)
    ts.sort()
    print(name, "p50 ms:", round(statistics.median(ts)), "p95 ms:", round(ts[int(0.95 * (len(ts) - 1))]))
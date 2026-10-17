import sys
import time

from docpilot.agent.graph import graph

for q in sys.argv[1:]:
    t = time.perf_counter()
    out = graph.invoke({"question": q})
    dt = time.perf_counter() - t
    print("Q:", q)
    print("decision:", out["decision"], "| retried:", out.get("retried"),
          "| trusted:", out.get("retry_trusted"), "| refused_by:", repr(out["refused_by"]))
    print("answer:", out["answer"])
    print("verify:", out["verify"])
    print("sources:", out["sources"])
    print(f"seconds: {dt:.1f}\n")
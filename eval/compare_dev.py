import json
import re
import statistics

CITE = re.compile(r"\[(\d+)\]")


def load(p):
    with open(p, encoding="utf-8") as f:
        return {r["id"]: r for r in json.load(f)}

def pct(v, q):
    v = sorted(v)
    return v[min(len(v) - 1, int(round(q * (len(v) - 1))))]

def cites(r):
    valid = {s["n"] for s in r["sources"]}
    c = {int(n) for n in CITE.findall(r["answer"])}
    return c, valid

naive = load("eval/results/answers_dev.json")
agent = load("eval/results/answers_dev_agent.json")

for name, d in (("naive", naive), ("agent", agent)):
    rows = list(d.values())
    ans = [r for r in rows if r["answerable"]]
    no = [r for r in rows if not r["answerable"]]
    gen = [r for r in rows if not r["refused"]]
    nocite = sum(1 for r in gen if r["sources"] and not cites(r)[0])
    badcite = sum(1 for r in gen if cites(r)[0] - cites(r)[1])
    lat = [r["latency_ms"] for r in rows]
    print(name,
          "| unans refused", sum(r["refused"] for r in no), "of", len(no),
          "| ans wrongly refused", sum(r["refused"] for r in ans), "of", len(ans),
          "| generated", len(gen), "no_citation", nocite, "bad_citation", badcite,
          "| p50", round(statistics.median(lat)), "p95", pct(lat, 0.95))

print("\nrows where refused differs:")
for i in naive:
    if naive[i]["refused"] != agent[i]["refused"]:
        print(i, "naive", naive[i]["refused"], naive[i]["refused_by"],
              "| agent", agent[i]["refused"], agent[i]["refused_by"])
print("\nrows where refused_by differs:")
for i in naive:
    if naive[i]["refused_by"] != agent[i]["refused_by"]:
        print(i, naive[i]["refused_by"], "->", agent[i]["refused_by"])
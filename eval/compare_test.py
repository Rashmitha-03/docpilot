import json
import re

CITE = re.compile(r"\[(\d+)\]")


def load(p):
    with open(p, encoding="utf-8") as f:
        return {r["id"]: r for r in json.load(f)}


def cites(r):
    return ({int(n) for n in CITE.findall(r["answer"])},
            {s["n"] for s in r["sources"]})


naive = load("eval/results/answers_test_naive.json")
agent = load("eval/results/answers_test_agent.json")

for name, d in (("naive", naive), ("agent", agent)):
    rows = list(d.values())
    gen = [r for r in rows if not r["refused"]]
    print(name, "| generated", len(gen),
          "| no_citation", sum(1 for r in gen if r["sources"] and not cites(r)[0]),
          "| bad_citation", sum(1 for r in gen if cites(r)[0] - cites(r)[1]))

print("\nrefused differs:", [i for i in naive if naive[i]["refused"] != agent[i]["refused"]])
print("refused_by differs:", [i for i in naive if naive[i]["refused_by"] != agent[i]["refused_by"]])
print("retried rows:", [i for i, r in agent.items() if r.get("retried")])
print("trusted rows:", [i for i, r in agent.items() if r.get("trusted")])
print("verify flags:", {i: r["verify"] for i, r in agent.items() if r.get("verify")})
same = [i for i in naive if naive[i]["answer"] == agent[i]["answer"]]
print("identical answer text:", len(same), "of", len(naive))
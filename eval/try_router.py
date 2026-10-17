import json

from docpilot.agent.nodes import route

with open("eval/dev.jsonl", encoding="utf-8") as f:
    rows = [json.loads(line) for line in f if line.strip()]

counts = {}
for r in rows:
    d = route(r["question"])
    counts[d] = counts.get(d, 0) + 1
    if d != "docs":
        print("NOT docs:", r["id"], r["question"])
print("dev routing:", counts)

print()
print("hand-picked cases (not a measured eval):")
for q in ["hi", "Thanks!", "thank you", "Hello there", "",
          "thanks, how do I add a header?", "What is OpenAPI?"]:
    print(f"  {route(q):9} <- {q!r}")

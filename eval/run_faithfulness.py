import json

import ollama

from docpilot.retrieval import hybrid

SYS = (
    "You check whether an ANSWER is supported by PASSAGES. Reply with one word: "
    "SUPPORTED if every factual claim in the answer is stated in the passages, "
    "otherwise UNSUPPORTED."
)

d = json.load(open("eval/results/answers_dev.json", encoding="utf-8"))
rows = [o for o in d if o["answerable"] and not o["refused"]]
res = []
for o in rows:
    hits = hybrid.search(o["question"], k=5)
    same = [(h.file, h.anchor) for h in hits] == [(s["file"], s["anchor"]) for s in o["sources"]]
    if not same:
        print(o["id"], "MISMATCH (skipped)")
        continue
    ctx = "\n\n".join(f"[{i}] {h.text}" for i, h in enumerate(hits, 1))
    user = f"PASSAGES:\n{ctx}\n\nANSWER:\n{o['answer']}"
    r = ollama.chat(model="llama3.2:3b", options={"temperature": 0},
                    messages=[{"role": "system", "content": SYS},
                              {"role": "user", "content": user}])
    raw = r["message"]["content"].strip()
    up = raw.upper()
    v = "UNSUPPORTED" if up.startswith("UNSUPPORTED") else "SUPPORTED" if up.startswith("SUPPORTED") else "UNCLEAR"
    res.append({"id": o["id"], "verdict": v, "raw": raw[:200]})
    print(o["id"], v)

json.dump(res, open("eval/results/faith_dev.json", "w", encoding="utf-8"), indent=2)
print("judged:", len(res), "| supported:", sum(x["verdict"] == "SUPPORTED" for x in res),
      "| unsupported:", sum(x["verdict"] == "UNSUPPORTED" for x in res),
      "| unclear:", sum(x["verdict"] == "UNCLEAR" for x in res))
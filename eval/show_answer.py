import json
import os

d = json.load(open("eval/results/answers_dev.json", encoding="utf-8"))
o = next(x for x in d if x["id"] == os.environ["QID"])
print("Q:", o["question"])
print("GOLD:", [(g["file"], g["anchor"]) for g in o["gold"]])
for s in o["sources"]:
    print(s["n"], s["file"], s["anchor"] or "(no anchor)")
print("ANSWER:", o["answer"])
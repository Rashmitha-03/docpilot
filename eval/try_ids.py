import os

import ollama

from docpilot.generation.answer import answer
from docpilot.generation.prompts import REFUSAL
from docpilot.retrieval import hybrid
from eval.run_eval import DEV, load_rows

ids = os.environ["IDS"].split(",")
for r in load_rows(DEV):
    if r["id"] not in ids:
        continue
    res = answer(r["question"])
    out = res["answer"]
    kind = "answerable" if r["answerable"] else "unanswerable"
    print(r["id"], kind, "->", "REFUSED" if out == REFUSAL else "ANSWERED")
    print("   ", out[:160].replace("\n", " "))
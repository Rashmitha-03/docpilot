import os

import ollama

from docpilot.generation.prompts import REFUSAL, build_messages
from docpilot.retrieval import hybrid
from eval.run_eval import DEV, load_rows

ids = os.environ["IDS"].split(",")
for r in load_rows(DEV):
    if r["id"] not in ids:
        continue
    msgs, _ = build_messages(r["question"], hybrid.search(r["question"], k=5))
    resp = ollama.chat(model="llama3.2:3b", messages=msgs, options={"temperature": 0})
    out = resp["message"]["content"].strip()
    kind = "answerable" if r["answerable"] else "unanswerable"
    print(r["id"], kind, "->", "REFUSED" if out == REFUSAL else "ANSWERED")
    print("   ", out[:160].replace("\n", " "))
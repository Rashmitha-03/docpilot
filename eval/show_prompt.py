from docpilot.generation.prompts import build_messages
from docpilot.retrieval import hybrid

q = "Can my path operation function be a normal function instead of async def?"
messages, sources = build_messages(q, hybrid.search(q, k=5))
print(messages[0]["content"])
print("---")
for s in sources:
    print(s["n"], s["file"], s["anchor"] or "(no anchor)", "|", s["header"])
print("user message chars:", len(messages[1]["content"]))
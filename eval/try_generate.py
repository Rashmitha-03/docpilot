import ollama

from docpilot.generation.prompts import build_messages
from docpilot.retrieval import hybrid

q = "Can my path operation function be a normal function instead of async def?"
messages, sources = build_messages(q, hybrid.search(q, k=5))
resp = ollama.chat(model="llama3.2:3b", messages=messages, options={"temperature": 0})
print(resp["message"]["content"])
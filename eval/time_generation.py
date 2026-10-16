import ollama

from docpilot.generation.prompts import build_messages
from docpilot.generation.answer import MODEL
from docpilot.retrieval import hybrid

QUESTIONS = [
    "How do I make a query parameter required in FastAPI?",
    "How do I add CORS middleware?",
    "How do I use background tasks?",
]

for run, q in enumerate(QUESTIONS, 1):
    msgs, _ = build_messages(q, hybrid.search(q, k=5))
    r = ollama.chat(model=MODEL, messages=msgs, options={"temperature": 0})
    s = 1e9
    print(f"run {run}: {q}")
    print(f"  load           {r['load_duration'] / s:6.1f} s")
    print(f"  prompt tokens  {r['prompt_eval_count']:6d}   took {r['prompt_eval_duration'] / s:6.1f} s")
    print(f"  output tokens  {r['eval_count']:6d}   took {r['eval_duration'] / s:6.1f} s")
    print(f"  total          {r['total_duration'] / s:6.1f} s")
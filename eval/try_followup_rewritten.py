from docpilot.generation.answer import answer
from docpilot.generation.rewrite import rewrite_question

history = [("user", "How do I declare a query parameter with a default value?")]
follow_up = "What about making it required?"

standalone = rewrite_question(history, follow_up)
print("REWRITTEN:", standalone)

result = answer(standalone)
print("refused_by:", result["refused_by"])
print("answer:", result["answer"])
print("sources:")
for s in result["sources"]:
    print("  ", {k: v for k, v in s.items() if "text" not in k})
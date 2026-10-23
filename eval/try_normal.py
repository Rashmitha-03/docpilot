from docpilot.generation.answer import answer

QS = [
    "Which URL shows the automatic Swagger UI documentation for my app?",
    "How do I declare a query parameter with a default value?",
    "How do I add CORS middleware?",
]
for q in QS:
    res = answer(q)
    print("Q:", q)
    print("refused_by:", res["refused_by"])
    print("answer:", res["answer"][:200])
    print()
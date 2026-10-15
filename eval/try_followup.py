from docpilot.generation.answer import answer

QUESTIONS = [
    "How do I declare a query parameter with a default value?",
    "What about making it required?",
]


def show(q):
    print("=" * 70)
    print("Q:", q)
    result = answer(q)
    print("refused_by:", result["refused_by"])
    print("answer:", result["answer"])
    print("sources:")
    for s in result["sources"]:
        if isinstance(s, dict):
            print("  ", {k: v for k, v in s.items() if "text" not in k})
        else:
            print("  ", s)


for q in QUESTIONS:
    show(q)
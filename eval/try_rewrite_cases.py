from docpilot.generation.rewrite import rewrite_question

CASES = [
    ("topic change",
     [("user", "How do I declare a query parameter with a default value?")],
     "How do I use background tasks?"),
    ("first turn",
     [],
     "How do I use background tasks?"),
    ("chained follow-up",
     [("user", "How do I set a response header?"),
      ("user", "What about doing it for cookies?")],
     "And how do I delete it?"),
    ("vague, no new topic",
     [("user", "How do I add CORS middleware?")],
     "Why is that needed?"),
    ("shorthand",
     [("user", "How do I declare a path parameter?")],
     "and with a type?"),
]

for name, history, q in CASES:
    print(f"[{name}]")
    print("  IN :", q)
    print("  OUT:", rewrite_question(history, q))
from docpilot.generation.rewrite import rewrite_question

h = [("user", "How do I declare a query parameter with a default value?")]
print("no history :", rewrite_question([], "What about making it required?"))
print("with history:", rewrite_question(h, "What about making it required?"))
from docpilot.generation.answer import answer

h = [("user", "How do I declare a query parameter with a default value?")]
r = answer("What about making it required?", history=h)
print("standalone:", r["standalone"])
print("refused_by:", r["refused_by"])
print("answer:", r["answer"])
print("sections:", sorted({(s["file"], s["anchor"]) for s in r["sources"]}))
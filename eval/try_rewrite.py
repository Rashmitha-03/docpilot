import ollama
import time

SYSTEM = (
    "You rewrite follow-up questions into standalone search queries. "
    "Use the chat history to replace pronouns and vague references "
    "(it, that, this, they) with the specific topic. "
    "Keep what the follow-up asks about: its new words must appear in the output. "
    "Output ONLY the rewritten question on one line. "
    "Do not answer it. If the follow-up already names its own topic, "
    "repeat it unchanged and ignore the history.\n\n"
    "Example 1\n"
    "History: user: How do I set a cookie in FastAPI?\n"
    "Follow-up: What about deleting it?\n"
    "Standalone: How do I delete a cookie in FastAPI?\n\n"
    "Example 2\n"
    "History: user: How do I set a cookie in FastAPI?\n"
    "Follow-up: How do I read a request body?\n"
    "Standalone: How do I read a request body?\n\n"
    "Example 3\n"
    "History: user: How do I add CORS middleware?\n"
    "Follow-up: Can you show an example?\n"
    "Standalone: Show an example of adding CORS middleware in FastAPI."
    
)

CASES = [
    (
        [("user", "How do I declare a query parameter with a default value?")],
        "What about making it required?",
    ),
    (
        [("user", "How do I declare a query parameter with a default value?")],
        "How do I add a header parameter?",
    ),
    (
        [("user", "How do I use dependency injection in FastAPI?")],
        "Can you show an example?",
    ),
]


def rewrite(history, question):
    hist = "\n".join(f"{role}: {text}" for role, text in history)
    prompt = f"Chat history:\n{hist}\n\nFollow-up question: {question}\n\nStandalone question:"
    r = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        options={"temperature": 0},
    )
    return r["message"]["content"].strip()


for history, q in CASES:
    t = time.time()
    out = rewrite(history, q)
    print("IN :", q)
    print("OUT:", out)
    print(f"time: {time.time() - t:.1f}s")
    print("-" * 60)
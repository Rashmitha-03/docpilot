import ollama

from docpilot import config  # noqa: F401  (kept for later settings)

REWRITE_MODEL = "llama3.2:3b"

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


def rewrite_question(history, question):
    """history: list of (role, text) tuples, oldest first. Returns a standalone question."""
    user_turns = [text for role, text in history if role == "user"]
    if not user_turns:
        return question

    # Only the last 2 user questions: they carry the topic, and keep the call fast.
    hist = "\n".join(f"user: {t}" for t in user_turns[-2:])
    prompt = (
        f"Chat history:\n{hist}\n\n"
        f"Follow-up question: {question}\n\n"
        "Standalone question:"
    )
    r = ollama.chat(
        model=REWRITE_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        options={"temperature": 0},
    )
    out = r["message"]["content"].strip().splitlines()
    out = out[0].strip() if out else ""
    # Safety net: if the model returns nothing, fall back to the original question.
    return out or question
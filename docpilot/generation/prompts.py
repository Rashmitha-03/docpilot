"""Grounded prompt: numbered context, [n] citations, one exact refusal sentence."""

REFUSAL = "I could not find this in the FastAPI docs."

SYSTEM = (
    "You answer questions about FastAPI using ONLY the numbered context "
    "passages provided.\n"
    "Rules:\n"
    "1. Use only the context. Do not use outside knowledge.\n"
    "2. Cite every claim with the passage number in square brackets, "
    "like [1] or [2][3].\n"
    "3. A passage that says the same thing in different words still counts "
    "as support. Synonyms count.\n"
    f"4. If the context does not contain the answer, reply with exactly: {REFUSAL}\n"
    "Add nothing else to a refusal."
)


def _label(h):
    return f"{h.file}#{h.anchor}" if h.anchor else h.file


def build_messages(question, hits):
    """Return (messages, sources). sources[i] is the passage cited as [i+1]."""
    blocks = [f"[{i}] ({_label(h)})\n{h.text}" for i, h in enumerate(hits, 1)]
    user = "Context:\n\n" + "\n\n".join(blocks) + f"\n\nQuestion: {question}"
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user},
    ]
    sources = [
        {"n": i, "file": h.file, "anchor": h.anchor, "header": h.header}
        for i, h in enumerate(hits, 1)
    ]
    return messages, sources
import re

import ollama

from docpilot.thresholds import CE_THRESHOLD

CHITCHAT = re.compile(
    r"(hi|hello|hey|thanks|thank you|thx|bye|goodbye|ok|okay|cool|great)"
    r"( there)?( thanks)?"
)


def route(question: str) -> str:
    """Return 'chitchat' for greetings/thanks, otherwise 'docs'."""
    text = re.sub(r"[^a-z ]", "", (question or "").lower()).strip()
    if not text or CHITCHAT.fullmatch(text):
        return "chitchat"
    return "docs"


# Below WEAK_FLOOR retrieval is hopeless (retry is pointless).
# Between WEAK_FLOOR and CE_THRESHOLD it is weak (one retry is worth trying).
WEAK_FLOOR = 0.0


def grade(top_score: float) -> str:
    """Return 'strong', 'weak' or 'hopeless' from the top-1 cross-encoder score."""
    if top_score >= CE_THRESHOLD:
        return "strong"
    if top_score >= WEAK_FLOOR:
        return "weak"
    return "hopeless"


RETRY_SYSTEM = (
    "Rewrite the user's question as a short search query for technical "
    "documentation. Keep the key technical terms from the question and add "
    "the words the docs would likely use for the same ideas. "
    "Output only the query, nothing else."
)


def retry_query(question: str) -> str:
    """One LLM call: rewrite a weakly retrieved question into a search query."""
    resp = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {"role": "system", "content": RETRY_SYSTEM},
            {"role": "user", "content": question},
        ],
        options={"temperature": 0},
    )
    text = resp["message"]["content"].strip().strip('"')
    return text or question

CITE = re.compile(r"\[(\d+)\]")


def verify(answer: str, sources: list, refused: bool) -> list:
    """Code-only checks on a generated answer. Returns a list of flags."""
    flags = []
    if not (answer or "").strip():
        return ["empty"]
    if refused:
        return flags
    cited = {int(n) for n in CITE.findall(answer)}
    valid = {s["n"] for s in sources}
    if cited - valid:
        flags.append("bad_citation")
    if sources and not cited:
        flags.append("no_citation")
    return flags
import json

import httpx
from docpilot.generation import llm
from docpilot.agent.nodes import route
from docpilot.safety import pre_check
from docpilot.generation.answer import CE_THRESHOLD, MODEL
from docpilot.generation.prompts import REFUSAL, build_messages
from docpilot.generation.rewrite import rewrite_question
from docpilot.retrieval import hybrid, rerank

CHITCHAT_REPLY = "Hi! Ask me anything about the FastAPI docs."
OLLAMA_DOWN = "The language model server (Ollama) is not running. Start Ollama and try again."


def _sse(event, data):
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def stream_answer(question, history=None, k=5, threshold=CE_THRESHOLD):
    """Naive path as a generator of SSE strings. Same steps as answer(),
    plus a canned reply for greetings and clear errors if Ollama fails."""
    if route(question) == "chitchat":
        yield _sse("meta", {"refused_by": None, "sources": [], "standalone": question})
        yield _sse("token", CHITCHAT_REPLY)
        yield _sse("done", {})
        return
    try:
        question = rewrite_question(history or [], question)
        top = rerank.search(question, k=1)
        if not top or top[0].score < threshold:
            yield _sse("meta", {"refused_by": "gate", "sources": [], "standalone": question})
            yield _sse("token", REFUSAL)
            yield _sse("done", {})
            return
        hits = hybrid.search(question, k=k)
        msgs, sources = build_messages(question, hits)
        yield _sse("meta", {"refused_by": None, "sources": sources, "standalone": question})
        for piece in llm.chat(msgs, stream=True):
            yield _sse("token", piece)
    except (ConnectionError, httpx.ConnectError):
        yield _sse("error", OLLAMA_DOWN)
    except Exception as e:
        yield _sse("error", f"Generation failed: {type(e).__name__}")
    yield _sse("done", {})
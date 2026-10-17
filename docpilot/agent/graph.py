from typing import TypedDict

import ollama
from langgraph.graph import END, START, StateGraph

from docpilot.agent.nodes import grade, retry_query, route, verify
from docpilot.generation.answer import MODEL
from docpilot.generation.prompts import REFUSAL, build_messages
from docpilot.retrieval import hybrid, rerank

CHITCHAT_REPLY = "Hi! Ask me anything about the FastAPI docs."


class State(TypedDict, total=False):
    question: str
    route: str
    query: str
    score: float
    band: str
    retried: bool
    retry_trusted: bool
    decision: str
    answer: str
    refused_by: str
    sources: list
    verify: list


def route_node(s: State) -> State:
    return {"route": route(s["question"])}


def retrieve_node(s: State) -> State:
    top = rerank.search(s["question"], k=1)[0]
    return {"query": s["question"], "score": top.score, "retried": False,
            "retry_trusted": False}


def grade_node(s: State) -> State:
    return {"band": grade(s["score"])}


def retry_node(s: State) -> State:
    q2 = retry_query(s["question"])
    top2 = rerank.search(q2, k=1)[0]
    original = {(h.file, h.anchor) for h in hybrid.search(s["question"], k=5)}
    trusted = grade(top2.score) == "strong" and (top2.file, top2.anchor) in original
    update = {"retried": True, "retry_trusted": trusted}
    if trusted:
        update.update({"query": q2, "score": top2.score, "band": "strong"})
    return update


def finish_node(s: State) -> State:
    if s["route"] == "chitchat":
        return {"decision": "chitchat"}
    return {"decision": "answer" if s["band"] == "strong" else "refuse"}


def reply_node(s: State) -> State:
    """Turn the decision into a reply. Same generation path as answer.py."""
    if s["decision"] == "chitchat":
        return {"answer": CHITCHAT_REPLY, "refused_by": "", "sources": []}
    if s["decision"] == "refuse":
        return {"answer": REFUSAL, "refused_by": "gate", "sources": []}
    hits = hybrid.search(s["query"], k=5)
    msgs, sources = build_messages(s["question"], hits)
    resp = ollama.chat(model=MODEL, messages=msgs, options={"temperature": 0})
    out = resp["message"]["content"].strip()
    return {"answer": out, "refused_by": "model" if out == REFUSAL else "",
            "sources": sources}


def check_node(s: State) -> State:
    skip = s["decision"] != "answer" or s["refused_by"] == "model"
    return {"verify": verify(s["answer"], s["sources"], skip)}


def after_route(s: State) -> str:
    return "finish" if s["route"] == "chitchat" else "retrieve"


def after_grade(s: State) -> str:
    return "retry" if s["band"] == "weak" else "finish"


g = StateGraph(State)
g.add_node("route", route_node)
g.add_node("retrieve", retrieve_node)
g.add_node("grade", grade_node)
g.add_node("retry", retry_node)
g.add_node("finish", finish_node)
g.add_node("reply", reply_node)
g.add_node("check", check_node)
g.add_edge(START, "route")
g.add_conditional_edges("route", after_route, {"finish": "finish", "retrieve": "retrieve"})
g.add_edge("retrieve", "grade")
g.add_conditional_edges("grade", after_grade, {"retry": "retry", "finish": "finish"})
g.add_edge("retry", "finish")
g.add_edge("finish", "reply")
g.add_edge("reply", "check")
g.add_edge("check", END)

graph = g.compile()
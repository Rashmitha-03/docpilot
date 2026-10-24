import html
import json
import time

import httpx
import streamlit as st

import os
import sys
from pathlib import Path

# Make `docpilot` importable when the host runs this file from app/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

API = "http://127.0.0.1:8000"
try:
    for _k, _v in st.secrets.items():  # copy the host's secrets into the environment
        if isinstance(_v, (str, int, float)):
            os.environ.setdefault(_k, str(_v))
except Exception:
    pass  # no secrets file locally: fine
INPROC = os.getenv("DOCPILOT_INPROCESS") == "1"  # call the pipeline directly, no API server
REFUSAL = "I could not find this in the FastAPI docs."
# Placeholders: edit these to questions your corpus covers.
EXAMPLES = [
    "How do I declare a query parameter?",
    "How do I add OAuth2 authentication?",
    "How do I use dependencies?",
    "How do I handle CORS?",
]

st.set_page_config(page_title="DocPilot", page_icon="\U0001F4C4", layout="centered")

st.markdown("""<style>
.block-container {max-width: 820px; padding-top: 2rem;}
#MainMenu, footer {visibility: hidden;}
.dp-hero h1 {font-size: 2.3rem; margin: 0; background: linear-gradient(90deg, #6366f1, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
.dp-hero p {opacity: .7; margin: .3rem 0 1.2rem 0;}
.dp-badge {display: inline-block; padding: 2px 10px; margin-right: 6px; border-radius: 999px; font-size: .75rem; font-weight: 600; border: 1px solid rgba(99,102,241,.45); background: rgba(99,102,241,.12);}
.dp-badge.agent {border-color: rgba(6,182,212,.55); background: rgba(6,182,212,.12);}
.dp-badge.refused {border-color: rgba(245,158,11,.55); background: rgba(245,158,11,.14);}
.dp-src {border-left: 3px solid #6366f1; padding: .35rem .8rem; margin: .35rem 0; border-radius: 0 8px 8px 0; background: rgba(128,128,128,.08); font-size: .9rem;}
[data-testid="stSidebar"] {border-right: 1px solid rgba(128,128,128,.25);}
[data-testid="stSidebar"] .block-container {padding-top: 1rem;}
.dp-side-brand {display: flex; align-items: center; gap: .6rem; margin-bottom: .2rem;}
.dp-side-logo {width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; background: linear-gradient(135deg, #6366f1, #06b6d4);}
.dp-side-name {font-weight: 700; font-size: 1.15rem; line-height: 1.1;}
.dp-side-tag {font-size: .75rem; opacity: .65;}
.dp-label {font-size: .7rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; opacity: .55; margin: 1rem 0 .3rem 0;}
.dp-card {border: 1px solid rgba(128,128,128,.28); border-left: 3px solid #6366f1; border-radius: 10px; padding: .6rem .8rem; background: rgba(128,128,128,.07); font-size: .85rem; line-height: 1.4;}
.dp-card.agent {border-left-color: #06b6d4;}
.dp-fact {display: flex; justify-content: space-between; gap: .5rem; font-size: .82rem; padding: .25rem 0; border-bottom: 1px dashed rgba(128,128,128,.25);}
.dp-fact span:first-child {opacity: .65;}
.dp-fact span:last-child {text-align: right; font-weight: 600;}
</style>""", unsafe_allow_html=True)

st.markdown(
    '<div class="dp-hero"><h1>DocPilot</h1>'
    '<p>Ask questions about the FastAPI docs. Every answer cites its sources, '
    'and DocPilot says so when the docs do not cover the question.</p></div>',
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending" not in st.session_state:
    st.session_state.pending = None

MODE_INFO = {
    "naive": ("Naive", "Streams the answer live and remembers the chat."),
    "agent": ("Agent", "Routes the question, grades its own search and retries once if the search is weak. "
                       "No streaming and no chat memory."),
}

with st.sidebar:
    st.markdown(
        '<div class="dp-side-brand"><div class="dp-side-logo">\U0001F4C4</div>'
        '<div><div class="dp-side-name">DocPilot</div>'
        '<div class="dp-side-tag">Citation-first docs assistant</div></div></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="dp-label">Answer mode</div>', unsafe_allow_html=True)
    mode = st.radio("Answer mode", ["naive", "agent"],
                    format_func=lambda m: MODE_INFO[m][0], label_visibility="collapsed")
    st.markdown(f'<div class="dp-card {mode}">{MODE_INFO[mode][1]}</div>',
                unsafe_allow_html=True)

    st.markdown('<div class="dp-label">About</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="dp-fact"><span>Corpus</span><span>FastAPI docs</span></div>'
        '<div class="dp-fact"><span>Size</span><span>155 files, 1,372 chunks</span></div>'
        '<div class="dp-fact"><span>Retrieval</span><span>BM25 + vector (RRF)</span></div>'
        '<div class="dp-fact"><span>Model</span><span>llama3.2:3b, local CPU</span></div>',
        unsafe_allow_html=True,
    )
    st.caption("A small local model can make mistakes. Check the cited sources.")

    st.markdown('<div class="dp-label">Chat</div>', unsafe_allow_html=True)
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


def show_sources(sources):
    if sources:
        with st.expander(f"Sources ({len(sources)})"):
            for s in sources:
                st.markdown(
                    f'<div class="dp-src"><b>[{s["n"]}]</b> <code>{html.escape(s["file"])}</code>'
                    f' &rsaquo; {html.escape(s["header"])}</div>',
                    unsafe_allow_html=True,
                )


def show_debug(meta, text):
    if meta:
        with st.expander("Debug"):
            st.write("Mode:", meta.get("mode", "naive"))
            if meta.get("mode") == "agent":
                st.write("Verify flags:", meta.get("verify") or "none")
            st.write("Standalone question:", meta.get("standalone"))
            if meta.get("refused_by") == "gate":
                st.write("Refused by: gate (retrieval score below threshold)")
            elif text.strip() == REFUSAL:
                st.write("Refused by: model")
            else:
                st.write("Answered")


def show_footer(sources, meta, text):
    """Badges, sources, debug. Used for live answers AND chat history."""
    if not meta:
        return
    m = meta.get("mode", "naive")
    parts = [f'<span class="dp-badge {m}">{m}</span>']
    if meta.get("refused_by") == "gate" or text.strip() == REFUSAL:
        parts.append('<span class="dp-badge refused">refused</span>')
    if meta.get("seconds") is not None:
        parts.append(f'<span class="dp-badge">{meta["seconds"]} s</span>')
    st.markdown("".join(parts), unsafe_allow_html=True)
    show_sources(sources)
    show_debug(meta, text)


def stream_ask(question, history):
    """Yield ('meta', dict) once, then ('token', str) pieces."""
    body = {"question": question, "history": history}
    with httpx.stream("POST", f"{API}/ask/stream", json=body, timeout=300) as r:
        r.raise_for_status()
        event = None
        for line in r.iter_lines():
            if line.startswith("event: "):
                event = line[7:]
            elif line.startswith("data: ") and event in ("meta", "token", "error"):
                yield event, json.loads(line[6:])


def agent_ask(question):
    body = {"question": question, "mode": "agent"}
    r = httpx.post(f"{API}/ask", json=body, timeout=300)
    if r.status_code == 503:
        raise httpx.HTTPError(r.json().get("detail", "Service unavailable"))
    r.raise_for_status()
    return r.json()


if INPROC:
    def stream_ask(question, history):
        """Same ('meta' | 'token' | 'error', data) events as the API version, no HTTP."""
        from docpilot.api.schemas import AskRequest
        from docpilot.api.stream import stream_answer

        pairs = AskRequest(question=question, history=history).history
        for chunk in stream_answer(question, history=pairs):
            event = None
            for line in chunk.splitlines():
                if line.startswith("event: "):
                    event = line[7:]
                elif line.startswith("data: ") and event in ("meta", "token", "error"):
                    yield event, json.loads(line[6:])

    def agent_ask(question):
        from docpilot.agent.graph import graph

        try:
            res = graph.invoke({"question": question})
        except Exception as e:
            raise httpx.HTTPError(f"Agent failed: {type(e).__name__}")
        return {"answer": res["answer"], "refused_by": res["refused_by"] or None,
                "sources": res["sources"], "verify": res["verify"], "standalone": None}


if INPROC:
    def stream_ask(question, history):
        """Same ('meta' | 'token' | 'error', data) events as the API version, no HTTP."""
        from docpilot.api.schemas import AskRequest
        from docpilot.api.stream import stream_answer

        pairs = AskRequest(question=question, history=history).history
        for chunk in stream_answer(question, history=pairs):
            event = None
            for line in chunk.splitlines():
                if line.startswith("event: "):
                    event = line[7:]
                elif line.startswith("data: ") and event in ("meta", "token", "error"):
                    yield event, json.loads(line[6:])

    def agent_ask(question):
        from docpilot.agent.graph import graph

        try:
            res = graph.invoke({"question": question})
        except Exception as e:
            raise httpx.HTTPError(f"Agent failed: {type(e).__name__}")
        return {"answer": res["answer"], "refused_by": res["refused_by"] or None,
                "sources": res["sources"], "verify": res["verify"], "standalone": None}


typed = st.chat_input("Ask about FastAPI...")
q = st.session_state.pending or typed
st.session_state.pending = None

if not st.session_state.messages and not q:
    st.markdown("**Try asking:**")
    cols = st.columns(2)
    for i, ex in enumerate(EXAMPLES):
        if cols[i % 2].button(ex, key=f"ex{i}", use_container_width=True):
            st.session_state.pending = ex
            st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m["role"] == "assistant":
            show_footer(m.get("sources", []), m.get("meta", {}), m["content"])

if q:
    history = [] if mode == "agent" else [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
    ]
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.markdown(q)
    with st.chat_message("assistant"):
        box = st.empty()
        text, sources, meta = "", [], {}
        t0 = time.perf_counter()
        try:
            if mode == "agent":
                with st.spinner("Agent is working (no streaming, can take a minute)..."):
                    res = agent_ask(q)
                text, sources = res["answer"], res["sources"]
                meta = {**res, "mode": "agent"}
                box.markdown(text)
            else:
                box.markdown("*Searching the docs...*")
                for kind, data in stream_ask(q, history):
                    if kind == "error":
                        text += f"\n\n**Error:** {data}"
                        box.markdown(text)
                    elif kind == "meta":
                        sources = data["sources"]
                        meta = {**data, "mode": "naive"}
                    else:
                        text += data
                        box.markdown(text)
        except httpx.HTTPError as e:
            text = f"API error: {e}. Is the server running on port 8000?"
            box.markdown(text)
        if meta:
            meta["seconds"] = round(time.perf_counter() - t0, 1)
        show_footer(sources, meta, text)
        st.session_state.messages.append(
            {"role": "assistant", "content": text, "sources": sources, "meta": meta})
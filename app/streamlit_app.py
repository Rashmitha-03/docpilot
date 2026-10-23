import html
import json
import time

import httpx
import streamlit as st

API = "http://127.0.0.1:8000"
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

with st.sidebar:
    st.header("Settings")
    mode = st.radio("Mode", ["naive", "agent"])
    st.caption(
        "naive: streams the answer and remembers the chat.  \n"
        "agent: no streaming, no chat history, slower, retries weak searches."
    )
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
    r.raise_for_status()
    return r.json()


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
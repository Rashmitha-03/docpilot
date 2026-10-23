
import json

import httpx
import streamlit as st

API = "http://127.0.0.1:8000"
REFUSAL = "I could not find this in the FastAPI docs."

st.set_page_config(page_title="DocPilot", page_icon="📄")
st.title("DocPilot")
st.caption("Ask questions about the FastAPI docs. Answers cite their sources.")

if "messages" not in st.session_state:
    st.session_state.messages = []

mode = st.sidebar.radio("Mode", ["naive", "agent"])
st.sidebar.caption(
    "naive: streams, remembers the chat. "
    "agent: no streaming, no chat history, slower, retries weak searches."
)


def show_sources(sources):
    if sources:
        with st.expander(f"Sources ({len(sources)})"):
            for s in sources:
                st.markdown(f"**[{s['n']}]** `{s['file']}` > {s['header']}")

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


for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m["role"] == "assistant":
            show_sources(m.get("sources", []))
            show_debug(m.get("meta", {}), m["content"])

q = st.chat_input("Ask about FastAPI...")
if q:
    history = [{"role": m["role"], "content": m["content"]}
               for m in st.session_state.messages]
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.markdown(q)
    with st.chat_message("assistant"):
        box = st.empty()
        text, sources, meta = "", [], {}
        try:
            if mode == "agent":
                with st.spinner("Agent is working (no streaming, can take a minute)..."):
                    res = agent_ask(q)
                text, sources = res["answer"], res["sources"]
                meta = {**res, "mode": "agent"}
                box.markdown(text)
            events = [] if mode == "agent" else stream_ask(q, history)
            for kind, data in events:
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
            show_sources(sources)
        show_debug(meta, text)
        st.session_state.messages.append(
        {"role": "assistant", "content": text, "sources": sources, "meta": meta})
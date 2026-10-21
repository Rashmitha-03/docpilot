import json

import httpx
import streamlit as st

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="DocPilot", page_icon="📄")
st.title("DocPilot")
st.caption("Ask questions about the FastAPI docs. Answers cite their sources.")

if "messages" not in st.session_state:
    st.session_state.messages = []


def show_sources(sources):
    if sources:
        with st.expander(f"Sources ({len(sources)})"):
            for s in sources:
                st.markdown(f"**[{s['n']}]** `{s['file']}` > {s['header']}")


def stream_ask(question, history):
    """Yield ('meta', dict) once, then ('token', str) pieces."""
    body = {"question": question, "history": history}
    with httpx.stream("POST", f"{API}/ask/stream", json=body, timeout=300) as r:
        r.raise_for_status()
        event = None
        for line in r.iter_lines():
            if line.startswith("event: "):
                event = line[7:]
            elif line.startswith("data: ") and event in ("meta", "token"):
                yield event, json.loads(line[6:])


for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m["role"] == "assistant":
            show_sources(m.get("sources", []))

q = st.chat_input("Ask about FastAPI...")
if q:
    history = [{"role": m["role"], "content": m["content"]}
               for m in st.session_state.messages]
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.markdown(q)
    with st.chat_message("assistant"):
        box = st.empty()
        text, sources = "", []
        try:
            for kind, data in stream_ask(q, history):
                if kind == "meta":
                    sources = data["sources"]
                else:
                    text += data
                    box.markdown(text)
        except httpx.HTTPError as e:
            text = f"API error: {e}. Is the server running on port 8000?"
            box.markdown(text)
        show_sources(sources)
    st.session_state.messages.append(
        {"role": "assistant", "content": text, "sources": sources})
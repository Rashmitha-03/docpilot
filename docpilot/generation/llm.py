"""One place that calls the language model. LLM_PROVIDER picks 'ollama' (default) or 'groq'."""
import json
import os

import httpx
import ollama
from dotenv import load_dotenv

load_dotenv()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def provider():
    return os.getenv("LLM_PROVIDER", "ollama").lower()


def _groq_body(messages, temperature, stream):
    return {
        "model": os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        "messages": messages,
        "temperature": temperature,
        "stream": stream,
    }


def _groq_headers():
    return {"Authorization": "Bearer " + os.getenv("GROQ_API_KEY", "")}


def _groq_stream(messages, temperature):
    try:
        with httpx.stream("POST", GROQ_URL, headers=_groq_headers(), timeout=120,
                          json=_groq_body(messages, temperature, True)) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    delta = json.loads(line[6:])["choices"][0]["delta"]
                    if delta.get("content"):
                        yield delta["content"]
    except httpx.ConnectError as e:
        raise ConnectionError(str(e))


def chat(messages, stream=False, temperature=0, model=None):
    """Return the full answer text, or a generator of text pieces when stream=True."""
    if provider() == "groq":
        if stream:
            return _groq_stream(messages, temperature)
        try:
            r = httpx.post(GROQ_URL, headers=_groq_headers(), timeout=120,
                           json=_groq_body(messages, temperature, False))
            r.raise_for_status()
        except httpx.ConnectError as e:
            raise ConnectionError(str(e))
        return r.json()["choices"][0]["message"]["content"] or ""
    model = model or os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    opts = {"temperature": temperature}
    if stream:
        return (p["message"]["content"] for p in
                ollama.chat(model=model, messages=messages, stream=True, options=opts)
                if p["message"]["content"])
    return ollama.chat(model=model, messages=messages, options=opts)["message"]["content"]
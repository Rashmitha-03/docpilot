import time

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from docpilot.api.schemas import AskRequest, AskResponse
from docpilot.api.stream import OLLAMA_DOWN
from docpilot.safety import pre_check
from docpilot.utils.cache import LRUCache, make_key
from docpilot.utils.logging import log_request
app = FastAPI(title="DocPilot")
_cache = LRUCache(max_size=128)


@app.get("/health")
def health():
    return {"status": "ok"}

def _run_model(req):
    if req.mode == "agent":
        from docpilot.agent.graph import graph

        res = graph.invoke({"question": req.question})
        return AskResponse(
            answer=res["answer"],
            refused_by=res["refused_by"] or None,
            sources=res["sources"],
            standalone=None,
            verify=res["verify"],
        )
    from docpilot.generation.answer import answer

    res = answer(req.question, history=req.history)
    return AskResponse(
        answer=res["answer"],
        refused_by=res["refused_by"],
        sources=res["sources"],
        standalone=res["standalone"],
    )


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    t = time.perf_counter()
    pc = pre_check(req.question)
    if pc:
        out = AskResponse(answer=pc["reply"],
                          refused_by="safety" if pc["kind"] == "blocked" else None)
        log_request(endpoint="/ask", mode=req.mode, q_len=len(req.question),
                    refused_by=out.refused_by, n_sources=0, verify=[], cache_hit=False,
                    pre_check=pc["category"], seconds=round(time.perf_counter() - t, 4))
        return out
    key = make_key(req.question, req.mode) if not req.history else None
    if key:
        cached = _cache.get(key)
        if cached is not None:
            out = AskResponse(**cached)
            log_request(endpoint="/ask", mode=req.mode, q_len=len(req.question),
                        refused_by=out.refused_by, n_sources=len(out.sources),
                        verify=out.verify, cache_hit=True,
                        seconds=round(time.perf_counter() - t, 4))
            return out
    try:
        out = _run_model(req)
    except (ConnectionError, httpx.ConnectError):
        raise HTTPException(status_code=503, detail=OLLAMA_DOWN)
    if key:
        _cache.set(key, out.model_dump())
    log_request(endpoint="/ask", mode=req.mode, q_len=len(req.question),
                refused_by=out.refused_by, n_sources=len(out.sources),
                verify=out.verify, cache_hit=False,
                seconds=round(time.perf_counter() - t, 2))
    return out

def _logged_stream(req):
    from docpilot.api.stream import stream_answer

    t = time.perf_counter()
    try:
        yield from stream_answer(req.question, history=req.history)
    finally:
        log_request(endpoint="/ask/stream", mode="naive", q_len=len(req.question),
                    seconds=round(time.perf_counter() - t, 2))


@app.post("/ask/stream")
def ask_stream(req: AskRequest):
    return StreamingResponse(_logged_stream(req), media_type="text/event-stream")
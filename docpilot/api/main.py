import time

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from docpilot.api.schemas import AskRequest, AskResponse
from docpilot.utils.logging import log_request

app = FastAPI(title="DocPilot")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    t = time.perf_counter()
    if req.mode == "agent":
        from docpilot.agent.graph import graph

        res = graph.invoke({"question": req.question})
        out = AskResponse(
            answer=res["answer"],
            refused_by=res["refused_by"] or None,
            sources=res["sources"],
            standalone=None,
            verify=res["verify"],
        )
    else:
        from docpilot.generation.answer import answer

        res = answer(req.question, history=req.history)
        out = AskResponse(
            answer=res["answer"],
            refused_by=res["refused_by"],
            sources=res["sources"],
            standalone=res["standalone"],
        )
    log_request(endpoint="/ask", mode=req.mode, q_len=len(req.question),
                refused_by=out.refused_by, n_sources=len(out.sources),
                verify=out.verify, seconds=round(time.perf_counter() - t, 2))
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
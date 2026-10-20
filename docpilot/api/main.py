from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from docpilot.api.schemas import AskRequest, AskResponse

app = FastAPI(title="DocPilot")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
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
    
@app.post("/ask/stream")
def ask_stream(req: AskRequest):
    from docpilot.api.stream import stream_answer

    return StreamingResponse(stream_answer(req.question, history=req.history),
                             media_type="text/event-stream")
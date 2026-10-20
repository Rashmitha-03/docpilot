from pydantic import BaseModel, Field


class Source(BaseModel):
    n: int
    file: str
    anchor: str
    header: str


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    history: list[dict] = Field(default_factory=list)  # used only by the naive path
    mode: str = Field(default="naive", pattern="^(naive|agent)$")


class AskResponse(BaseModel):
    answer: str
    refused_by: str | None = None
    sources: list[Source] = Field(default_factory=list)
    standalone: str | None = None
    verify: list[str] = Field(default_factory=list)
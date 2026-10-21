from pydantic import BaseModel, Field, field_validator


class Source(BaseModel):
    n: int
    file: str
    anchor: str
    header: str


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    history: list = Field(default_factory=list)  # used only by the naive path
    mode: str = Field(default="naive", pattern="^(naive|agent)$")

    @field_validator("history")
    @classmethod
    def history_as_pairs(cls, v):
        """Accept {"role","content"} dicts or [role, text] pairs; return (role, text) tuples."""
        out = []
        for item in v:
            if isinstance(item, dict):
                out.append((item.get("role", ""), item.get("content", "")))
            else:
                out.append((item[0], item[1]))
        return out


class AskResponse(BaseModel):
    answer: str
    refused_by: str | None = None
    sources: list[Source] = Field(default_factory=list)
    standalone: str | None = None
    verify: list[str] = Field(default_factory=list)
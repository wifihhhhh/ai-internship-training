from pydantic import BaseModel, ConfigDict, Field


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    quote: str = Field(min_length=1)

class AnswerDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str = Field(min_length=1)
    supported: bool
    evidence: list[Evidence] = Field(default_factory=list)

class Source(BaseModel):
    chunk_id: str
    source: str
    quote: str

class RagAnswer(BaseModel):
    question: str
    answer: str
    supported: bool
    sources: list[Source]
    retrieved_count: int
    elapsed_ms: float
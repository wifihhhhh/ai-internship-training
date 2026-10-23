from pydantic import BaseModel, ConfigDict, Field, StrictBool


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    quote: str = Field(min_length=1, max_length=400)

class Brief(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=80)
    body: str = Field(min_length=1, max_length=3000)
    supported: bool
    citations: list[Citation] = Field(
        default_factory=list,
        max_length=6,
    )

class Review(BaseModel):
    model_config = ConfigDict(extra="forbid")

    passed: bool
    issues: list[str] = Field(
        default_factory=list,
        max_length=5
    )

class ApprovalDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approved: StrictBool
    digest: str = Field(pattern=r"^[0-9a-f]{64}$") # 必须是64位小写十六进制哈希串


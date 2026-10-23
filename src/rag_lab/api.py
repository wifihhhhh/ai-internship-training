import logging
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from langchain_core.exceptions import OutputParserException
from openai import APIError
from pydantic import BaseModel, Field, field_validator

from src.rag_lab.retrieval import KnowledgeBaseEmptyError
from src.rag_lab.schemas import RagAnswer
from src.rag_lab.service import ask


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["rag"])

class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    k: int = Field(default=3, ge=1, le=6)
    

    @field_validator("question")
    @classmethod
    def reject_blank(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("问题不能为空白")

        return value

@router.post("/ask", response_model=RagAnswer)
def ask_endpoint(request: QuestionRequest) -> RagAnswer:
    trace_id = uuid4().hex[:12]

    try:
        result = ask(request.question, k=request.k)

        logger.info(
            "rag trace=%s supported=%s hits=%s elapsed_ms=%s",
            trace_id,
            result.supported,
            result.retrieved_count,
            result.elapsed_ms,
        )

        return result
    except KnowledgeBaseEmptyError as exc:
        raise HTTPException(
            status_code=503,
            detail="知识库为空，请先导入资料",
        ) from exc
    
    except (APIError, OutputParserException, ValueError) as exc:
        logger.error(
            "rag failed trace=%s type=%s",
            trace_id,
            type(exc).__name__,
        )

        raise HTTPException(
            status_code=502,
            detail={
                "message": "知识库问答失败，请检查服务器日志",
                "trace_id": trace_id,
            },
        ) from exc
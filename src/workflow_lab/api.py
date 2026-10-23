import logging
from functools import lru_cache
from threading import Lock
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from src.rag_lab.schemas import RagAnswer
from src.workflow_lab.graph import build_graph


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/workflow", tags=["workflow"])

# 本地学习演示串行执行，避免同一内存会话并发修改。
workflow_lock = Lock()

@lru_cache(maxsize=1)
def get_graph():
    return build_graph()

class WorlflowRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    session_id: str = Field(
        default_factory=lambda: uuid4().hex,
        min_length=1,
        max_length=100,
    )

    @field_validator("question")
    @classmethod
    def reject_blank(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("问题不能为空白")

        return value

class WorkflowResponse(BaseModel):
    session_id: str
    resolved_question: str
    retries: int
    result: RagAnswer

@router.post("/ask", response_model=WorkflowResponse)
def workflow_endpoint(request: WorlflowRequest):
    try:
        config = {
            "configurable": {
                "thread_id": request.session_id,
            },
            "recursion_limit": 20,
        }

        with workflow_lock:
            state = get_graph().invoke(
                {"question": request.question},
                config,
            )

        return WorkflowResponse(
            session_id=request.session_id,
            resolved_question=state["question"],
            retries=state["attempts"],
            result=state["result"],
        )

    except Exception as exc:
        logger.error(
            "workflow failed type=%s",

            type(exc).__name__,
        )

        raise HTTPException(
            status_code=502,
            detail="工作流执行失败，请检查服务器日志",
        ) from exc
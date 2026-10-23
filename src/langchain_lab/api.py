import logging

from fastapi import APIRouter, HTTPException
from langchain_core.exceptions import OutputParserException
from openai import APIError
from pydantic import BaseModel, Field, field_validator

from src.langchain_lab.schemas import TaskDraft
from src.langchain_lab.service import extract_task


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/langchain",
    tags=["langchain"],
)

class ExtractionRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

    @field_validator("message")
    @classmethod
    def reject_blank_message(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("message不能只包含空格")

        return value

@router.post("/extract", response_model=TaskDraft)
def extract_task_endpoint(request: ExtractionRequest) -> TaskDraft:
    """调用真实千问，返回任务草稿，不直接修改数据库"""
    try:
        return extract_task(request.message)

    except OutputParserException as exc:
        logger.warning("千问输出未通过结构化解析")
        raise HTTPException(
            status_code=502,
            detail="模型输出格式不符合要求，请重试",
        ) from exc

    except APIError as exc:
        logger.error(
            "千问API调用失败：type=%s status=%s",
            type(exc).__name__,
            getattr(exc, "status_code", None),
        )
        raise HTTPException(
            status_code=502,
            detail="模型服务调用失败，请检查配置、网络和账号状态",
        ) from exc

    except ValueError as exc:
        logger.error("模型本地配置或参数错误：%s", type(exc).__name__)
        raise HTTPException(
            status_code=503,
            detail="模型服务配置不完整，请检查服务器配置",
        ) from exc
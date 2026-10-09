from datetime import date
from enum import Enum

from pydantic import BaseModel, Field

class TaskIntent(str, Enum):
    """模型可选择的任务意图"""
    CREATE_TASK = "create_task"
    QUERY_TASK = "query_task"
    OTHER = "other"

class TaskExtraction(BaseModel):
    """经过程序验证后的任务提取结果"""

    intent: TaskIntent
    title: str | None = Field(
        default=None,
        max_length=120,
    )
    priority: int | None = Field(
        default=None,
        ge=1,
        le=5
    )
    due_date: date | None = None
    needs_clarification: bool
    clarification_question: str | None = Field(
        default=None,
        max_length=200,
    )
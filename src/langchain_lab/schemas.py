from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

class TaskDraft(BaseModel):
    """提取结果，不是已保存的数据库任务"""
    model_config = ConfigDict(extra="forbid")

    intent: Literal["create_task", "query_task", "other"]

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    priority: int | None = Field(
        default=None,
        ge=1,
        le=3,
        description="1高、2中、3低；未说明时为null",
    )

    needs_clarification: bool = False

    @model_validator(mode="after")
    def validate_create_task(self):
        if self.intent == "create_task":
            if not self.needs_clarification:
                if self.title is None or not self.title.strip():
                    raise ValueError("无需澄清的创建任务必须有有效标题")

        return self
from typing import Any
from pydantic import BaseModel, Field

class ToolCall(BaseModel):
    """模型或规划器提出的一次工具调用请求"""
    tool_name: str = Field(
        min_length=1,
        description="要调用的已注册工具名称",
    )
    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description="传给工具的参数",
    )

class AddInput(BaseModel):
    """加法工具的输入规则"""
    a: float
    b: float

class MultiplyInput(BaseModel):
    """乘法工具的输入规则"""
    a: float
    b: float

class CurrentDateInput(BaseModel):
    """获取日期不需要参数，保留空模型以统一接口"""

class ListOpenTasksInput(BaseModel):
    """查询未完成任务时允许的参数"""
    limit: int = Field(default=10, ge=1, le=50,)

class GetTaskInput(BaseModel):
    """按 ID 查询任务的输入规则"""
    task_id: int = Field(ge=1)

class DeleteTaskInput(BaseModel):
    """删除任务的输入规则"""
    task_id: int = Field(ge=1)
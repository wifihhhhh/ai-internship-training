from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel, ValidationError

from src.tool_agent.schemas import ToolCall

class ToolNotFoundError(ValueError):
    """请求了没有注册的工具时抛出"""

class ToolArgumentsError(ValueError):
    """工具参数未通过 Pydantic 校验时抛出"""

@dataclass(frozen=True)
class ToolDefinition:
    """描述一个允许 Agent 使用的工具"""
    name: str
    description: str
    input_model: type[BaseModel]
    handler: Callable[..., dict[str, Any]]
    requires_approval: bool = False

class ToolRegistry:
    """只允许调用显式注册过的工具"""
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        self._tools[tool.name] = tool

    def get(self, tool_name: str) -> ToolDefinition:
        tool = self._tools.get(tool_name)

        if tool is None:
            raise ToolNotFoundError(
                f"Tool is not registered: {tool_name}"
            )

        return tool

    def describe_tools(self) -> list[dict[str, Any]]:
        """返回可给模型阅读的工具定义"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.input_model.model_json_schema(),
                "requires_approval": tool.requires_approval,
            } for tool in self._tools.values()
        ]

    def execute(self, tool_call: ToolCall) -> dict[str, Any]:
        """验证参数后执行指定工具"""
        tool = self.get(tool_call.tool_name)
        try: 
            # 先将不可信 arguments 校验为可信 Pydantic 对象。
            validated_input = tool.input_model.model_validate(
                tool_call.arguments
            )
        except ValidationError as error:
            raise ToolArgumentsError(f"Invalid arguments for {tool.name}") from error

        return tool.handler(**validated_input.model_dump())
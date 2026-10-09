from typing import Any
from src.tool_agent.planner import ToolPlanner
from src.tool_agent.registry import ToolRegistry

class ToolAgent:
    """协调规划器和工具注册表"""
    def __init__(
            self,
            planner: ToolPlanner,
            registry: ToolRegistry,
    ) -> None:
        self.planner = planner
        self.registry = registry

    def run(self, user_input: str) -> dict[str, Any]:
        tool_call = self.planner.plan(user_input)

        if tool_call is None:
            return {
                "status": "no_tool_selected",
                "message": "当前无法确定应调用哪个工具。",
            }

        tool = self.registry.get(tool_call.tool_name)

        if tool.requires_approval:
            return {
                "status": "approval_required",
                "tool_name": tool.name,
                "arguments": tool_call.arguments,
                "message": "敏感操作等待人工确认。",
            }

        output = self.registry.execute(tool_call)

        return {
            "status": "completed",
            "tool_name": tool.name,
            "arguments":tool_call.arguments,
            "output": output
        }
import re
from typing import Protocol

from src.tool_agent.schemas import ToolCall

class ToolPlanner(Protocol):
    """规划器负责决定调用哪个工具，不负责真正执行。"""
    def plan(
            self, 
            user_input: str,
    ) -> ToolCall | None:
        """根据用户输入返回工具调用申请。"""

class RuleBasedPlanner:
    """用于学习的简单规划器，后续可替换为真实 LLM"""
    def plan(
            self, 
            user_input: str,
    ) -> ToolCall | None:
        normalized = user_input.lower().strip()

        if "今天" in user_input or "日期" in user_input:
            return ToolCall(
                tool_name="get_current_date",
                arguments={"limit": 10},
            )

        if "未完成任务" in user_input:
            return ToolCall(
                tool_name="list_open_tasks",
                arguments={"limit": 10},
            )

        # 仅匹配如 “3 + 12” 的简单形式。
        match = re.fullmatch(
            r"\s*(\d+(?:\.\d+)?)\s*\+\s*(\d+(?:\.\d+)?)\s*", 
            user_input,
        )
        if match is not None:
            return ToolCall(
                tool_name="add_numbers",
                arguments={
                    "a": float(match.group(1)),
                    "b": float(match.group(2)),
                },
            )

        return None

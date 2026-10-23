from langchain.agents import create_agent

from src.langchain_lab.models import build_real_model
from src.langchain_lab.tools import TOOLS


def build_tool_agent():
    return create_agent(
        model=build_real_model(),
        tools=TOOLS,
        system_prompt=(
            "你是学习助手。"
            "算术问题使用计算工具，日期问题使用日期工具。"
            "根据真实工具结果回答，获得足够信息后停止调用。"
        )
    )
from langchain_core.tools import tool
from src.tool_agent.schemas import AddInput, CurrentDateInput, MultiplyInput
from src.tool_agent.tools import (
    add_numbers as calculate_sum,
    get_current_date as read_date,
    multiply_numbers as calculate_product
)

@tool("add_numbers", args_schema=AddInput)
def add_numbers_tool(a: float, b: float) -> dict[str, float]:
    "计算两数之和"
    return calculate_sum(a=a, b=b)

@tool("multiply_numbers", args_schema=MultiplyInput)
def multiply_numbers_tool(a: float, b: float) -> dict[str, float]:
    "计算两数之积"
    return calculate_product(a=a, b=b)

@tool("get_current_date", args_schema=CurrentDateInput)
def current_date_tool() -> dict[str, str]:
    """查询程序运行当天的日期，无需输入参数"""
    return read_date

TOOLS = [
    add_numbers_tool,
    multiply_numbers_tool,
    current_date_tool,
]

TOOLS_BY_NAME = {item.name: item for item in TOOLS}
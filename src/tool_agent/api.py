from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.tool_agent.agent import ToolAgent
from src.tool_agent.planner import RuleBasedPlanner
from src.tool_agent.registry import ToolDefinition, ToolRegistry
from src.tool_agent.schemas import AddInput, CurrentDateInput, MultiplyInput
from src.tool_agent.tools import add_numbers, get_current_date, multiply_numbers

router = APIRouter(
    prefix="/agent",
    tags=["tool-agent"],
)

class AgentRequest(BaseModel):
    """用户提交给工具 Agent 的自然语言请求"""

    message: str = Field(
        min_length=1,
        max_length=500,
    )

def build_agent() -> ToolAgent:
    """集中注册允许使用的工具"""
    registry = ToolRegistry()

    registry.register(
        ToolDefinition(
            name="add_numbers",
            description="计算两个数字的和。",
            input_model=AddInput,
            handler=add_numbers,
        )
    )

    registry.register(
        ToolDefinition(
            name="multiply_numbers",
            description="计算两个数字的乘积。",
            input_model=MultiplyInput,
            handler=multiply_numbers,
        )
    )

    registry.register(
        ToolDefinition(
            name="get_current_date",
            description="获取今天日期。",
            input_model=CurrentDateInput,
            handler=get_current_date,
        )
    )

    return ToolAgent(
        planner=RuleBasedPlanner(),
        registry=registry,
    )

agent = build_agent()

@router.post("/run")
def run_agent(request: AgentRequest) -> dict:
    """接收自然语言请求并返回工具执行结果"""
    return agent.run(request.message)
import json
from src.tool_agent.registry import ToolDefinition, ToolRegistry
from src.tool_agent.schemas import AddInput, CurrentDateInput, MultiplyInput, ToolCall, DeleteTaskInput
from src.tool_agent.tools import add_numbers, get_current_date, multiply_numbers

registry = ToolRegistry()

registry.register(
    ToolDefinition(
        name='add_numbers',
        description="计算两个数字的和",
        input_model=AddInput,
        handler=add_numbers,
    )
)

registry.register(
    ToolDefinition(
        name="multiply_numbers",
        description="计算两个数字的乘积",
        input_model=MultiplyInput,
        handler=multiply_numbers,
    )
)

registry.register(
    ToolDefinition(
        name="get_current_date",
        description="获取今天日期",
        input_model=CurrentDateInput,
        handler=get_current_date,
    )
)

registry.register(
    ToolDefinition(
        name="delete_task",
        description="删除指定任务。该操作必须由人工确认。",
        input_model=DeleteTaskInput,
        handler=lambda task_id: {
            "message": (f"任务 {task_id} 已通过审批后才也许删除。")
        },
        requires_approval=True,
    )
)

tool_call = ToolCall(
    tool_name="multiply_numbers",
    arguments={"a": 3, "b": 12},
)

result = registry.execute(tool_call)

print("=== 可用工具 Schema ===")
print(json.dumps(registry.describe_tools(), ensure_ascii=False, indent=2))

print("\n=== 工具执行结果 ===")
print(json.dumps(result, ensure_ascii=False, indent=2))
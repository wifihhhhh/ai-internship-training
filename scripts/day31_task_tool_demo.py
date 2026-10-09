import json

from src.tool_agent.task_tools import get_task_by_id, list_open_tasks

print("=== 未完成任务 ===")
print(
    json.dumps(
        list_open_tasks(limit=5),
        ensure_ascii=False,
        indent=2,
    )
)
print("\n=== ID 为 1 的任务 ===")
print(
    json.dumps(
        get_task_by_id(task_id=1),
        ensure_ascii=False,
        indent=2,
    )
)
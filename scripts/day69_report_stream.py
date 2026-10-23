from uuid import uuid4

from src.report_lab.graph import build_graph


def main() -> None:
    task_id = uuid4().hex

    for update in build_graph().stream(
        {
            "task_id": task_id,
            "question": "根据笔记，整理Function Calling的执行边界。",
            "revision": 0,
        },
        {
            "configurable": {"thread_id": task_id},
            "recursion_limit": 30,
        },
        stream_mode="updates",
    ):
        for node, changes in update.items():
            print("完成角色或节点：", node)
            print("更新字段：", list(changes))

if __name__ == "__main__":
    main()
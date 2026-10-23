import json
from uuid import uuid4

from src.report_lab.graph import build_graph


def main() -> None:
    task_id = uuid4().hex
    graph = build_graph()

    state = graph.invoke(
        {
            "task_id": task_id,
            "question": "根据学习笔记，整理Redis缓存失效学习简报。",
            "revision": 0,
        },
        {
            "configurable": {"thread_id": task_id},
            "recursion_limit": 30,
        },
    )

    print("状态：", state["status"])
    print("修订次数：", state["revision"])
    print("搜索次数：", state["search_calls"])
    print("草稿：")
    print(json.dumps(state["draft"], ensure_ascii=False, indent=2))
    print("审查：", state["review"])

if __name__ == "__main__":
    main()
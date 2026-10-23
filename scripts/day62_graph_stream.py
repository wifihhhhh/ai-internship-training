from uuid import uuid4

from src.workflow_lab.graph import build_graph


def main() -> None:
    graph = build_graph()

    config = {
        "configurable": {"thread_id": uuid4().hex},
        "recursion_limit": 20,
    }

    for update in graph.stream(
        {"question": "明天北京会不会下雨？"},
        config,
        stream_mode="updates",
    ):
        for node_name, changes in update.items():
            print("完成节点：", node_name)
            print("更新字段：", list(changes))

if __name__ == "__main__":
    main()
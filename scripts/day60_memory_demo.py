from src.workflow_lab.graph import build_graph

def main() -> None:
    graph = build_graph()

    config = {
        "configurable": {"thread_id": "tina-demo"},
        "recursion_limit": 20,
    }

    first = graph.invoke(
        {"question": "Redis缓存任务列表有什么作用？"},
        config,
    )
    print("第一轮：", first["result"]["answer"])

    second = graph.invoke(
        {"question": "修改任务后它为什么可能还是旧的？"},
        config,
    )

    print("独立问题：", second["question"])
    print("第二轮：", second["result"]["answer"])

    snapshot = graph.get_state(config)
    print("保存历史轮数：", len(snapshot.values["history"]))

if __name__ == "__main__":
    main()
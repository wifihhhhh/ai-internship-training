from src.workflow_lab.graph import build_graph


def main() -> None:
    graph = build_graph()

    state = graph.invoke({
        "question": "Function Calling由谁执行工具？",
    })

    print(state["result"])

if __name__ == "__main__":
    main()
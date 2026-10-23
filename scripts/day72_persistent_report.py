from uuid import uuid4

from src.report_lab.persistence import open_graph


def main() -> None:
    task_id = uuid4().hex

    with open_graph() as graph:
        graph.invoke(
            {
                "task_id": task_id,
                "question": "整理Python虚拟环境学习简报。",
                "revision": 0,
            },{
                "configurable": {"thread_id": task_id},
                "recursion_limit": 30,
            },
        )

    # 关闭旧连接，再重新读取状态。
    with open_graph() as graph:
        snapshot = graph.get_state({
            "configurable": {"thread_id": task_id}
        })

        print("任务ID:", task_id)
        print("保存状态：", snapshot.values["status"])

if __name__ == "__main__":
    main()
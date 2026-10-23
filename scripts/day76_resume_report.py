from uuid import UUID

from langgraph.types import Command

from src.report_lab.persistence import open_graph

def main() -> None:
    task_id = UUID(input("输入之前保存的任务ID：").strip()).hex

    config = {
        "configurable": {"thread_id": task_id},
        "recursion_limit": 30,
    }

    with open_graph() as graph:
        snapshot = graph.get_state(config)

        pending = [
            item.value
            for task in snapshot.tasks
            for item in task.interrupts
        ]

        if not pending:
            print("该任务没有等待审批的中断。")
            print("状态：", snapshot.values.get("status"))
            return

        print(pending[0]["preview"])

        approved = input("输入 yes 批准，其他输入拒绝：") == "yes"

        result = graph.invoke(
            Command(resume={
                "approved": approved,
                "digest": pending[0]["digest"],
            }),
            config,
        )

        print("status:", result["status"])
        print("export:", result.get("artifact_path", "无"))

if __name__ == "__main__":
    main()
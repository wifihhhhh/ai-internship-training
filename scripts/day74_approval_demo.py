from uuid import uuid4

from langgraph.types import Command

from src.report_lab.persistence import open_graph


def main() -> None:
    task_id = uuid4().hex

    config = {
        "configurable": {"thread_id": task_id},
        "recursion_limit": 30,
    }

    with open_graph() as graph:
        result = graph.invoke(
            {
                "task_id": task_id,
                "question": "根据笔记整理Redis缓存失效简报。",
                "revision": 0,
            },
            config
        )

        print("任务ID：", task_id)

        interruptions = result.get("__interrupt__", ())

        if not interruptions:
            print("没有进入审批：", result.get("status"))
            print(result.get("review"))
            return

        pending = interruptions[0].value
        print(pending["preview"])

        approved = input("输入 yes 批准导出，其他输入表示拒绝：") == "yes"

        final = graph.invoke(
            Command(resume={
                "approved": approved,
                "digest": pending["digest"],
            }),
            config,
        )

        print("result:", final["status"])
        print("document:", final.get("artifact_path", "unexported"))

if __name__ == "__main__":
    main()
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]  

def target(intent, title=None, priority=None, clarify=False):
    return {
        "intent": intent,
        "title": title,
        "priority": priority,
        "needs_clarification": clarify,
    }

def build_rows(topics, template, queries, chats):
    rows = []

    priorities = [
        ("，优先级高", 1),
        ("，优先级中", 2),
        ("，优先级低", 3),
        ("", None),
    ]

    for topic in topics:
        for suffix, priority in priorities:
            rows.append({
                "input": template.format(title=topic) + suffix,
                "target": target(
                    "create_task",
                    title=topic,
                    priority=priority,
                ),
            })

    for text in queries:
        rows.append({
            "input": text,
            "target": target("query_task"),
        })

    for text in chats:
        rows.append({
            "input": text,
            "target": target("other"),
        })

    rows.append({
        "input": "帮我添加一个任务",
        "target": target("create_task", clarify=True),
    })

    return rows

def main() -> None:
    output = ROOT / "data" / "sft"
    # 允许复用上次失败留下的空目录，但不覆盖已有数据。
    if output.exists() and any(output.iterdir()):
        raise ValueError("data/sft不是空目录，请先检查已有数据，避免覆盖")

    datasets = {
        "train": build_rows(
            [
                "学习Redis", "复习MySQL", "整理README",
                "练习Git", "学习FastAPI", "练习Python",
            ],
            "添加任务：{title}",
            ["查询任务", "列出未完成任务", "看看任务列表"],
            ["你好", "谢谢", "今天心情不错"],
        ),
        "validation": build_rows(
            ["理解SQLAlchemy", "练习pytest"],
            "请记下这件事：{title}",
            ["请展示我的任务", "有哪些没完成的任务"],
            ["早上好", "辛苦了"],
        ),
        "test": build_rows(
            ["学习Chroma", "理解LangGraph"],
            "帮我建立一个任务，内容是{title}",
            ["把任务清单给我看看", "我想查看未完成事项"],
            ["晚上好", "感谢帮助"],
        ),
    }

    seen = set()

    # 先完成所有数据的检查，再创建目录和写文件。
    for split, rows in datasets.items():
        for row in rows:
            if row["input"] == "帮我添加一个任务":
                row["input"] = {
                    "train": "帮我添加一个任务",
                    "validation": "我想新增事项，但是还没想好内容",
                    "test": "创建一项任务，具体内容暂时不确定",
                }[split]

            if row["input"] in seen:
                raise ValueError(
                    f"发现重复输入：split={split}，input={row['input']}"
                )

            seen.add(row["input"])

    output.mkdir(parents=True, exist_ok=True)

    # 每个数据集分别保存，不能放到循环外面。
    for split, rows in datasets.items():
        path = output / f"{split}.jsonl"

        path.write_text(
            "\n".join(
                json.dumps(row, ensure_ascii=False)
                for row in rows
            ) + "\n",
            encoding="utf-8",
        )

        print(split, len(rows))

if __name__ == "__main__":
    main()
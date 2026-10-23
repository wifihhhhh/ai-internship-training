from src.langchain_lab.chains import build_task_extraction_chain
from src.langchain_lab.models import build_real_model

def main() -> None:
    chain = build_task_extraction_chain(build_real_model())

    examples = [
        "添加任务：学习 Redis，优先级高",
        "添加任务：整理 README",
        "帮我添加一个任务",
        "查询未完成任务",
        "你好呀",
    ]

    for text in examples:
        print("\n用户输入：", text)

        result = chain.invoke({"message": text})

        print("返回类型：", type(result).__name__)
        print(result.model_dump_json(indent=2))

if __name__ == "__main__":
    main()
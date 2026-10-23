from langchain_core.messages import HumanMessage, SystemMessage

from src.langchain_lab.chains import build_explain_chain
from src.langchain_lab.models import build_real_model

def main() -> None:
    model = build_real_model()
    chain = build_explain_chain(model)

    # 一：真实流式输出。
    print("流式回答：")

    for chunk in chain.stream({
        "level": "初学",
        "topic": "数据库索引",
    }):
        print(chunk, end="", flush=True)

    print("\n")

    # 二：多个独立问题的批量调用。
    results = chain.batch(
        [
            {"level": "初学", "topic": "MySQL"},
            {"level": "初学", "topic": "Redis"},
        ],
        config={"max_concurrency": 2},
    )

    for index, result in enumerate(results, start=1):
        print(f"批量结果 {index}：")
        print(result)

    # 三：把真实上一轮回答加入下一轮历史。
    history = [
        SystemMessage(content="你是学习助手，回答简洁。"),
        HumanMessage(content="我叫h，正在学习LangChain。")
    ]

    first_response = model.invoke(history)
    history.append(first_response)

    history.append(
        HumanMessage(content="我叫什么？我在学习什么？")
    )

    second_response = model.invoke(history)
    print("\n带历史回答：", second_response.content)

if __name__ == "__main__":
    main()
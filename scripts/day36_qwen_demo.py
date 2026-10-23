from time import perf_counter

from langchain_core.messages import HumanMessage, SystemMessage

from src.langchain_lab.models import build_real_model

def main() -> None:
    model = build_real_model()

    messages = [
        SystemMessage(content="你是 Python 老师，回答简洁易懂。"),
        HumanMessage(content="用两句话解释 Python 虚拟环境，并举一个用途。")
    ]

    start = perf_counter()
    response = model.invoke(messages)
    elapsed = perf_counter() - start

    print("message type:", type(response).__name__)
    print("model response:", response.content)
    print("token usage:", response.usage_metadata)
    print(f"duration: {elapsed:.2f} s")

if __name__ == "__main__":
    main()
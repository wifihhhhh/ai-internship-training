from src.langchain_lab.chains import build_explain_chain
from src.langchain_lab.models import build_real_model

def main() -> None:
    model = build_real_model()
    chain = build_explain_chain(model)

    result = chain.invoke({
        "level": "准备后端实习面试",
        "topic": "RESTful API",
    })

    print("返回类型：", type(result).__name__)
    print(result)

if __name__ == "__main__":
    main()
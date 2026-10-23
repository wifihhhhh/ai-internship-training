from src.langchain_lab.agent import build_tool_agent

def main() -> None:
    agent = build_tool_agent()

    result = agent.invoke(
        {
            "messages": [{
                "role": "user",
                "content": "先计算3加12，再把结果乘以2。"
            }]
        },
        config={"recursion_limit": 16},
    )

    for message in result["messages"]:
        print("\n消息类型：", message.type)

        if getattr(message, "tool_calls", None):
            print("工具请求：", message.tool_calls)

        print("内容：", message.content)

if __name__ == "__main__":
    main()
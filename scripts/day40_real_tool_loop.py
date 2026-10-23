import json
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from src.langchain_lab.models import build_real_model
from src.langchain_lab.tools import TOOLS, TOOLS_BY_NAME

def main() -> None:
    model = build_real_model().bind_tools(TOOLS)

    messages = [
        SystemMessage(
            content=(
                "你是计算助手。算术必须调用工具，"
                "日期必须调用日期工具。"
                "拿到足够结果后直接回答，不重复调用。"
            )
        ),
        HumanMessage(content="先计算3加12，再把结果乘以2。")
    ]

    # 限制模型决策轮次，避免流程无限继续。
    for round_number in range(1, 7):
        response = model.invoke(messages)
        messages.append(response)

        print(f"\n第 {round_number} 轮")

        if not response.tool_calls:
            print("最终回答：", response.content)
            response

        for call in response.tool_calls:
            name = call["name"]

            if name not in TOOLS_BY_NAME:
                raise ValueError(f"不允许调用未注册工具：{name}")

            selected_tool = TOOLS_BY_NAME[name]
            output = selected_tool.invoke(call["args"])

            print("工具名称：", name)
            print("调用参数：", call["args"])
            print("执行结果：", output)

            messages.append(
                ToolMessage(
                    content=json.dumps(output, ensure_ascii=False),
                    tool_call_id=call["id"],
                )
            )

    raise RuntimeError("达到最大决策轮次，Agent仍未完成")

if __name__ == "__main__":
    main()
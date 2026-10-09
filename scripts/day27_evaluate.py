import json

from src.prompt_lab.client import MockLLMClient
from src.prompt_lab.evaluation import evaluate_cases, summarize_results
from src.prompt_lab.evaluation_cases import CASES

# 当前使用 Mock LLM，只验证评估流程是否正常。
# 接入真实模型后，只需替换这里的客户端。
results = evaluate_cases(
    cases=CASES,
    llm_client=MockLLMClient(),
)

summary = summarize_results(results)

print("=== 评估汇总 ===")
print(json.dumps(summary, ensure_ascii=False, indent=2))

print("\n=== 每条样例结果 ===")
for result in results:
    print(
        f"{result['name']}: "
        f"parse={result['parse_ok']}, "
        f"intent={result['intent_ok']}, "
        f"priority={result['priority_ok']}, "
        f"date={result['due_date_ok']}, "
        f"clarification={result['clarification_ok']}"
    )
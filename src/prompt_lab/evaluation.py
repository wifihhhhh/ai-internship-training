from dataclasses import dataclass
from datetime import date

from src.prompt_lab.client import LLMClient
from src.prompt_lab.parsing import LLMOutputError
from src.prompt_lab.schemas import TaskIntent
from src.prompt_lab.service import extract_task


@dataclass(frozen=True)
class EvaluationCase:
    """一条人工标注好的测试题。"""

    name: str
    user_input: str
    expected_intent: TaskIntent
    expected_priority: int | None
    expected_due_date: date | None
    expected_needs_clarification: bool


def evaluate_cases(
    cases: list[EvaluationCase],
    llm_client: LLMClient,
) -> list[dict[str, object]]:
    """逐条调用模型，并记录是否符合预期。"""

    results: list[dict[str, object]] = []

    for case in cases:
        try:
            actual = extract_task(case.user_input, llm_client)

            # 日期对象转为字符串，便于输出 JSON 和人工阅读。
            actual_due_date = (
                actual.due_date.isoformat()
                if actual.due_date is not None
                else None
            )

            results.append(
                {
                    "name": case.name,
                    "input": case.user_input,
                    "parse_ok": True,
                    "intent_ok": (
                        actual.intent == case.expected_intent
                    ),
                    "priority_ok": (
                        actual.priority == case.expected_priority
                    ),
                    "due_date_ok": (
                        actual.due_date == case.expected_due_date
                    ),
                    "clarification_ok": (
                        actual.needs_clarification
                        == case.expected_needs_clarification
                    ),
                    "actual": actual.model_dump(mode="json"),
                    "error": None,
                }
            )

        except LLMOutputError as error:
            # 模型返回非法 JSON 或不符合 Pydantic 规则时，
            # 不让整个评估中断，而是记录这条失败。
            results.append(
                {
                    "name": case.name,
                    "input": case.user_input,
                    "parse_ok": False,
                    "intent_ok": False,
                    "priority_ok": False,
                    "due_date_ok": False,
                    "clarification_ok": False,
                    "actual": None,
                    "error": str(error),
                }
            )

    return results


def summarize_results(
    results: list[dict[str, object]],
) -> dict[str, int]:
    """统计各项测试通过数量。"""

    total = len(results)

    return {
        "total": total,
        "parse_ok": sum(
            result["parse_ok"] is True
            for result in results
        ),
        "intent_ok": sum(
            result["intent_ok"] is True
            for result in results
        ),
        "priority_ok": sum(
            result["priority_ok"] is True
            for result in results
        ),
        "due_date_ok": sum(
            result["due_date_ok"] is True
            for result in results
        ),
        "clarification_ok": sum(
            result["clarification_ok"] is True
            for result in results
        ),
    }
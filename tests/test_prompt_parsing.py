import pytest

from src.prompt_lab.parsing import LLMOutputError, parse_task_extraction

def test_parse_valid_task_extraction() -> None:
    result = parse_task_extraction(
        """{
          "intent": "create_task",
          "title": "完成 FastAPI 测试",
          "priority": 1,
          "due_date": "2026-10-06",
          "needs_clarification": false,
          "clarification_question": null
        }"""
    )

    assert result.title == "完成 FastAPI 测试"
    assert result.priority == 1
    assert result.needs_clarification is False

def test_reject_invalid_priority() -> None:
    with pytest.raises(LLMOutputError):
        parse_task_extraction("""{
            "intent": "create_task",
            "title": "不合理任务",
            "priority": 10,
            "due_date": null,
            "needs_clarification": false,
            "clarification_question": null
        }""")
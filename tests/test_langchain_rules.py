import pytest
from pydantic import ValidationError

from src.langchain_lab.schemas import TaskDraft


def test_invalid_priority_is_rejected() -> None:
    with pytest.raises(ValidationError):
        TaskDraft(
            intent="create_task",
            title="学习LangChain",
            priority=99,
            needs_clarification=False,
        )

def test_create_without_title_requires_clarification() -> None:
    with pytest.raises(ValidationError):
        TaskDraft(
            intent="create_task",
            title=None,
            needs_clarification=False,
        )
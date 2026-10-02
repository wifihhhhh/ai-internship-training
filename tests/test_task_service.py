import pytest

from src.exceptions import TaskNotFoundError
from src.task_service import get_task

def test_get_existing_task() -> None:
    task = get_task(1)
    assert task.id == 1
    assert task.title == "完成 Day 4"

def test_get_missing_task_raises_error() -> None:
    with pytest.raises(TaskNotFoundError) as error:
        get_task(999)
    assert error.value.task_id == 999
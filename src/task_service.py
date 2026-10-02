from src.exceptions import TaskNotFoundError
from src.logging_config import get_logger
from src.task import Task

logger = get_logger(__name__)

TASKS: dict[int, Task] = {
    1: Task(id=1, title="完成 Day 4", priority=1),
}

def get_task(task_id: int) -> Task:
    """根据任务 ID 获取任务"""
    task = TASKS.get(task_id)

    if task is None:
        logger.warning("Task was not found: task_id=%s", task_id)
        raise TaskNotFoundError(task_id)
    
    logger.info("Task found: task_id=%s", task_id)
    return task
# 定义业务异常

class TaskNotFoundError(Exception):
    """请求的任务不存在时抛出"""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} was not found.")
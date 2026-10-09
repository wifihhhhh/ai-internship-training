from sqlalchemy import select

from src.database import SessionLocal
from src.models import Task

def list_open_tasks(limit: int = 10) -> dict[str, object]:
    """查询未完成任务，只读，不修改数据库"""
    with SessionLocal() as db:
        tasks = db.scalars(
            select(Task)
            .where(Task.completed.is_(False))
            .order_by(Task.priority, Task.id)
            .limit(limit)
        ).all()

        return {
            "count": len(tasks),
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "priority": task.priority,
                }
                for task in tasks
            ],
        }

def get_task_by_id(task_id: int) -> dict[str, object]:
    """按 ID 查询单个任务"""
    with SessionLocal() as db:
        task = db.get(Task, task_id)

        if task is None:
            return {
                "found": False,
                "task_id": task_id,
            }

        return {
            "found": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "completed": task.completed,
                "priority": task.priority,
            }
        }
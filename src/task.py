from dataclasses import dataclass
from datetime import date

@dataclass
class Task:
    id: int
    title: str
    completed: bool = False
    priority: int = 3
    due_date: date | None = None

    def complete(self) -> None:
        """标记任务为已完成。"""
        self.completed = True
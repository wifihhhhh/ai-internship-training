from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="AI Internship Training API",
    version="0.1.0",
    description="用于训练 FastAPI 与 RESTful API 的任务管理服务。",
)

TASKS: dict[int, dict] = {
    1: {
        "id": 1,
        "title": "学习 FastAPI",
        "completed": False,
        "priority": 1,
    },
    2: {
        "id": 2,
        "title": "完成 Git 练习",
        "completed": True,
        "priority": 2,
    },
}

@app.get("/health", tags=["system"])
def health() ->dict[str, str]:
    """健康检查接口"""
    return {"status": "ok"}

@app.get("/tasks", tags=["tasks"])
def list_tasks(
    completed: bool | None = None,
    q: str | None = None,
) -> list[dict]:
    """获取任务列表"""
    tasks = list(TASKS.values())
    if completed is not None:
        tasks = [task for task in tasks if task["completed"] == completed]
    if q is not None:
        keywords = q.lower()
        tasks = [task for task in tasks if keywords in task["title"].lower()]

    return tasks

@app.get("/tasks/{task_id}", tags=["tasks"])
def get_task(task_id: int) -> dict:
    """获取指定任务"""
    task = TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} was not found",)
    
    return task
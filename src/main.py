from fastapi import FastAPI, HTTPException, Query, status
from src.schemas import TaskCreate, TaskUpdate, TaskReplace, TaskResponse, TaskPage

app = FastAPI(
    title="AI Internship Training API",
    version="0.1.0",
    description="用于训练 FastAPI 与 RESTful API 的任务管理服务。",
)

INITIAL_TASKS: dict[int, TaskResponse] = {
    1: TaskResponse(
        id=1,
        title="学习 FastAPI",
        completed=False,
        priority=1,
    ),
    2: TaskResponse(
        id=2,
        title="完成 Git 练习",
        completed=True,
        priority=2,
    ),
}

TASKS: dict[int, TaskResponse] = {}
next_task_id = 1

def reset_tasks() -> None:
    """重置任务列表，恢复初始数据，主要用于测试。"""
    global next_task_id

    TASKS.clear()
    TASKS.update(INITIAL_TASKS)
    next_task_id = max(TASKS) + 1

def get_task_or_404(task_id: int) -> TaskResponse:
    """获取指定任务，如果不存在则抛出 404 异常"""
    task = TASKS.get(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} was not found",
        )
    return task

reset_tasks()


@app.get("/tasks", 
        response_model=TaskPage,
        tags=["tasks"]
        )
def list_tasks(
    completed: bool | None = None,
    q: str | None = Query(default=None, min_length=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
) -> TaskPage:
    tasks = list(TASKS.values())

    if completed is not None:
        tasks = [task for task in tasks if task.completed == completed]

    if q is not None:
        keyword = q.lower()
        tasks = [
            task
            for task in tasks
            if keyword in task.title.lower()
        ]

    total = len(tasks)
    start = (page - 1) * page_size
    end = start + page_size

    return TaskPage(
        items=tasks[start:end],
        page=page,
        page_size=page_size,
        total=total,
    )

@app.get("/tasks/{task_id}",
        response_model=TaskResponse,
        tags=["tasks"])
def get_task(task_id: int) -> TaskResponse:
    """获取指定任务"""
    return get_task_or_404(task_id)

@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["tasks"]
)

def create_task(payload: TaskCreate) -> TaskResponse:
    """创建新任务"""
    global next_task_id

    task = TaskResponse(
        id=next_task_id,
        title=payload.title,
        completed=False,
        priority=payload.priority,
    )
    TASKS[task.id] = task
    next_task_id += 1

    return task

@app.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["tasks"],
)
def replace_task(task_id: int, payload: TaskReplace) -> TaskResponse:
    get_task_or_404(task_id)

    task = TaskResponse(
        id=task_id,
        title=payload.title,
        completed=payload.completed,
        priority=payload.priority,
    )
    TASKS[task.id] = task

    return task

@app.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["tasks"],
)
def update_task(task_id: int, payload: TaskUpdate) -> TaskResponse:
    current_task = get_task_or_404(task_id)
    changes = payload.model_dump(exclude_unset=True)

    updated_task = current_task.model_copy(update=changes)
    TASKS[task_id] = updated_task

    return updated_task

@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["tasks"],
)
def delete_task(task_id: int) -> None:
    get_task_or_404(task_id)
    del TASKS[task_id]
from fastapi import Depends, FastAPI, HTTPException, Query, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from redis.exceptions import RedisError
from pathlib import Path
from fastapi.staticfiles import StaticFiles

from src.database import get_db
from src.models import Task
from src.schemas import TaskCreate, TaskUpdate, TaskReplace, TaskResponse, TaskPage
from src.cache import get_cache, make_task_list_cache_key, invalidate_task_list_cache
from src.logging_config import get_logger
from src.config import settings
from src.tool_agent.api import router as tool_agent_router
from src.langchain_lab.api import router as langchain_router
from src.rag_lab.api import router as rag_router
from src.workflow_lab.api import router as workflow_router

logger = get_logger(__name__)

app = FastAPI(
    title="AI Internship Training API",
    version="0.1.0",
    description="用于训练 FastAPI 与 RESTful API 的任务管理服务。",
)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
app.mount(
    "/rag-ui",
    StaticFiles(
        directory=str(PROJECT_ROOT / "frontend"),
        html=True,
    ),
    name="rag-ui",
)
app.include_router(tool_agent_router)
app.include_router(langchain_router)
app.include_router(rag_router)
app.include_router(workflow_router)

@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "database": "configured",
        "cache": (
            "enabled" 
            if settings.redis_enabled 
            else "disabled"
        )
    }

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

def get_task_or_404(db: Session, task_id: int) -> TaskResponse:
    """获取指定任务，如果不存在则抛出 404 异常"""
    task = db.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} was not found",
        )
    return task

reset_tasks()

@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}
@app.get("/tasks", 
        response_model=TaskPage,
        tags=["tasks"]
        )
def list_tasks(
    completed: bool | None = None,
    q: str | None = Query(default=None, min_length=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> TaskPage:
    cache = get_cache()
    cache_key = make_task_list_cache_key(completed, q, page, page_size,)

    if cache is not None:
        try:
            cached_value = cache.get(cache_key)

            if cached_value is not None:
                return TaskPage.model_validate_json(cached_value)
        except RedisError:
            logger.warning("Redis read failed; falling back to database", exc_info=True,)
    filters = []

    if completed is not None:
        filters.append(Task.completed == completed)

    if q is not None:
        filters.append(Task.title.ilike(f"%{q}%"))

    total_statement = select(func.count()).select_from(Task)
    task_statement = select(Task).order_by(Task.id)

    if filters:
        total_statement = total_statement.where(*filters)
        task_statement = task_statement.where(*filters)

    total = db.scalar(total_statement) or 0

    tasks = db.scalars(task_statement.offset((page - 1) * page_size).limit(page_size)).all()

    result = TaskPage(
        items=tasks,
        page=page,
        page_size=page_size,
        total=total,
    )

    if cache is not None:
        try:
            cache.setex(
                cache_key,
                settings.cache_ttl_seconds,
                result.model_dump_json(),
            )
        except RedisError:
            logger.warning("Redis write failed; response still succeeds", exc_info=True)

    return result
    
@app.get("/tasks/{task_id}",
        response_model=TaskResponse,
        tags=["tasks"])
def get_task(
    task_id: int,
    db: Session = Depends(get_db)
) -> TaskResponse:
    """获取指定任务"""
    return get_task_or_404(db, task_id)

@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["tasks"]
)

def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> Task:
    """创建新任务"""
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    invalidate_task_list_cache()
    db.refresh(task)

    return task

@app.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["tasks"],
)
def replace_task(
    task_id: int, 
    payload: TaskReplace, 
    db: Session = Depends(get_db)
) -> TaskResponse:
    task = get_task_or_404(db, task_id)

    task.title = payload.title
    task.completed = payload.completed
    task.priority = payload.priority

    db.commit()
    invalidate_task_list_cache()
    db.refresh(task)

    return task

@app.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["tasks"],
)
def update_task(
    task_id: int, 
    payload: TaskUpdate, 
    db: Session = Depends(get_db)
) -> Task:
    task = get_task_or_404(db, task_id)
    for field_name, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field_name, value)
    changes = payload.model_dump(exclude_unset=True)

    db.commit()
    invalidate_task_list_cache()
    db.refresh(task)

    return task

@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["tasks"],
)
def delete_task(
    task_id: int, 
    db: Session = Depends(get_db)
) -> None:
    task = get_task_or_404(db, task_id)
    db.delete(task)
    db.commit()
    invalidate_task_list_cache()

# 数据库错误处理器
@app.exception_handler(SQLAlchemyError)
async def handle_database_error(
    request: Request,
    error: SQLAlchemyError,
) -> JSONResponse:
    logger.exception("Database operation failed: %s", error,)

    return JSONResponse(
        status_code=503, # 服务暂时不可用
        content={"detail": "Database is temporarily unavailable"},
    )
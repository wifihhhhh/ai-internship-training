import logging
import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from threading import Lock
from uuid import UUID, uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from langgraph.types import Command
from pydantic import BaseModel, Field, field_validator

from src.report_lab.export import EXPORT_DIR
from src.report_lab.persistence import open_graph
from src.report_lab.schemas import ApprovalDecision


PROJECT_ROOT = Path(__file__).resolve().parents[2]
logger = logging.getLogger(__name__)

lock = Lock()
security = HTTPBearer(auto_error=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv(PROJECT_ROOT / ".env", override=True)

    token = os.getenv("REPORT_API_TOKEN", "").strip()

    if len(token) < 24:
        raise ValueError("REPORT_API_TOKEN至少设置24个字符")

    app.state.report_token = token

    with open_graph() as graph:
        app.state.report_graph = graph
        yield

app = FastAPI(
    title="学习简报助手",
    lifespan=lifespan,
)
app.mount(
    "/ui",
    StaticFiles(
        directory=str(PROJECT_ROOT / "report_frontend"),
        html=True,
    ),
    name="report-ui",
)

def require_token(
        request: Request,
        credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    if (
        credentials is None
        or not secrets.compare_digest(
            credentials.credentials,
            request.app.state.report_token,
        )
    ):
        raise HTTPException(status_code=401, detail="访问令牌无效")

class ReportRequest(BaseModel):
    question: str = Field(min_length=1, max_length=600)

    @field_validator("question")
    @classmethod
    def reject_blank(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("问题不能为空白")

        return value

def config_for(task_id: str) -> dict:
    return {
        "configurable": {"thread_id": task_id},
        "recursion_limit": 30,
    }

def inspect_task(graph, task_id: str) -> dict:
    snapshot = graph.get_state(config_for(task_id))

    if not snapshot.values:
        raise HTTPException(status_code=404, detail="task does not exist")

    pending = [
        item.value
        for task in snapshot.tasks
        for item in task.interrupts
    ]

    failed = any(task.error for task in snapshot.tasks)

    status = snapshot.values.get("status", "running")

    if pending:
        status = "awaiting_approval"
    elif failed:
        status = "failed"

    return {
        "task_id": task_id,
        "status": status,
        "draft": snapshot.values.get("draft"),
        "review": snapshot.values.get("review"),
        "approval": pending[0] if pending else None,
    }

@app.post("/tasks", dependencies=[Depends(require_token)])
def create_report(payload: ReportRequest, request: Request):
    task_id = uuid4().hex
    graph = request.app.state.report_graph

    try:
        with lock:
            graph.invoke(
                {
                    "task_id": task_id,
                    "question": payload.question,
                    "revision": 0,
                },
                config_for(task_id),
            )

            return inspect_task(graph, task_id)

    except Exception as exc:
        logger.error(
            "report failed task=%s type=%s",
            task_id,
            type(exc).__name__,
        )

        raise HTTPException(
            status_code=502,
            detail={
                "message": "报告生成失败",
                "task_id": task_id,
            },
        ) from exc

@app.get("/tasks/{task_id}", dependencies=[Depends(require_token)])
def get_report(task_id: UUID, request: Request):
    with lock:
        return inspect_task(
            request.app.state.report_graph,
            task_id.hex,
        )

@app.post(
    "/tasks/{task_id}/decision",
    dependencies=[Depends(require_token)]
)
def decide_report(
    task_id: UUID,
    decision: ApprovalDecision,
    request: Request,
):
    graph = request.app.state.report_graph

    with lock:
        current = inspect_task(graph, task_id.hex)

        if current["status"] != "awaiting_approval":
            raise HTTPException(
                status_code=409,
                detail="任务当前不在等待审批",
            )

        if decision.digest != current["approval"]["digest"]:
            raise HTTPException(
                status_code=409,
                detail="审批摘要与当前报告不一致",
            )

        try:
            graph.invoke(
                Command(resume=decision.model_dump()),
                config_for(task_id.hex)
            )
        except Exception as exc:
            logger.error(
                "decision failed task=%s type=%s",
                task_id.hex,
                type(exc).__name__,
            )
            raise HTTPException(
                status_code=502,
                detail="审批恢复失败，请检查日志",
            ) from exc

        return inspect_task(graph, task_id.hex)

@app.get(
    "/tasks/{task_id}/download",
    dependencies=[Depends(require_token)],
)
def download_report(task_id: UUID, request: Request):
    graph = request.app.state.report_graph

    with lock:
        snapshot = graph.get_state(config_for(task_id.hex))
        values = snapshot.values

        if values.get("status") != "exported":
            raise HTTPException(
                status_code=409,
                detail="任务尚未批准导出",
            )

        path = Path(values["artifact_path"]).resolve()

        if not path.is_relative_to(EXPORT_DIR.resolve()):
            raise HTTPException(
                status_code=500,
                detail="导出路径不合法",
            )

        if not path.is_file():
            raise HTTPException(
                status_code=404,
                detail="文件不存在"
            )

        return FileResponse(
            path,
            filename=path.name,
            media_type="text/markdown"
        )
from fastapi import FastAPI

app = FastAPI(
    title="AI Internship Training API",
    version="0.1.0",
    description="用于训练 FastAPI 与 RESTful API 的任务管理服务。"
)

@app.get("/health", tags=["system"])
def health() ->dict[str, str]:
    """健康检查接口"""
    return {"status": "ok"}
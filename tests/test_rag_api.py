from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.rag_lab.api import router


def build_client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

def test_blank_question_returns_422() -> None:
    with build_client() as client:
        response = client.post(
            "/rag/ask",
            json={"question": "   ", "k": 3},
        )

    assert response.status_code == 422

def test_invalid_k_returns_422() -> None:
    with build_client() as client:
        response = client.post(
            "/rag/ask",
            json={"question": "Redis是什么？", "k": 99},
        )

    assert response.status_code == 422
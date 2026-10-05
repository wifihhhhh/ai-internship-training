import pytest
from fastapi.testclient import TestClient

from src.main import app, reset_tasks

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_task_data() -> None:
    reset_tasks()


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_tasks() -> None:
    response = client.get("/tasks?page=1&page_size=10")

    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_create_task() -> None:
    response = client.post(
        "/tasks",
        json={
            "title": "编写接口测试",
            "priority": 2,
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["id"] == 3
    assert data["title"] == "编写接口测试"
    assert data["completed"] is False
    assert data["priority"] == 2


def test_create_task_rejects_invalid_priority() -> None:
    response = client.post(
        "/tasks",
        json={
            "title": "无效优先级任务",
            "priority": 9,
        },
    )

    assert response.status_code == 422


def test_get_missing_task_returns_404() -> None:
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_patch_task() -> None:
    response = client.patch(
        "/tasks/1",
        json={"completed": True},
    )

    assert response.status_code == 200
    assert response.json()["completed"] is True
    assert response.json()["title"] == "学习 FastAPI"


def test_delete_task() -> None:
    response = client.delete("/tasks/1")

    assert response.status_code == 204

    response = client.get("/tasks/1")
    assert response.status_code == 404
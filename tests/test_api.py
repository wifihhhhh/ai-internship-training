import os

os.environ["DATABASE_URL"] = "sqlite:///./data/test_tasks.db"
os.environ["REDIS_ENABLED"] = "false"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from src.database import Base, SessionLocal, engine
from src.main import app
from src.models import Task

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def create_test_schema() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def seed_tasks() -> None:
    with SessionLocal() as db:
        db.execute(delete(Task))
        db.add_all(
            [
                Task(
                    title="学习 FastAPI",
                    completed=False,
                    priority=1,
                ),
                Task(
                    title="完成 Git 练习",
                    completed=True,
                    priority=2,
                ),
            ]
        )
        db.commit()


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_tasks() -> None:
    response = client.get("/tasks?page=1&page_size=10")

    assert response.status_code == 200
    assert response.json()["total"] == 2


def test_create_task() -> None:
    response = client.post(
        "/tasks",
        json={
            "title": "编写数据库测试",
            "priority": 2,
        },
    )

    assert response.status_code == 201
    assert response.json()["title"] == "编写数据库测试"


def test_missing_task_returns_404() -> None:
    response = client.get("/tasks/999")

    assert response.status_code == 404


def test_patch_task() -> None:
    response = client.patch(
        "/tasks/1",
        json={"completed": True},
    )

    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_delete_task() -> None:
    response = client.delete("/tasks/1")

    assert response.status_code == 204

    response = client.get("/tasks/1")
    assert response.status_code == 404
from fastapi.testclient import TestClient

from app.main import app
from app.db import engine
from app.models import Base

client = TestClient(app)


def setup_module(module):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_create_and_get_task():
    response = client.post(
        "/tasks",
        json={"title": "Test task", "description": "Verify endpoint", "status": "todo"},
    )
    assert response.status_code == 201
    task = response.json()
    assert task["title"] == "Test task"
    task_id = task["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    task2 = response.json()
    assert task2["id"] == task_id
    assert task2["status"] == "todo"


def test_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert "Company-Grade Task API" in response.text
    assert "Load tasks" in response.text


def test_stats_endpoint():
    response = client.get("/tasks/stats")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total"] >= 1
    assert "todo" in stats["by_status"]

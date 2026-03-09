import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from fastapi.testclient import TestClient
from app import app, tasks, next_id


@pytest.fixture(autouse=True)
def reset_state():
    """Restaura el estado inicial antes de cada prueba."""
    global tasks, next_id
    tasks.clear()
    tasks.extend([
        {"id": 1, "title": "Aprender Jenkins", "done": False},
        {"id": 2, "title": "Configurar pipeline CI/CD", "done": False},
        {"id": 3, "title": "Desplegar en producción", "done": False},
    ])

    import app as app_module
    app_module.tasks = tasks
    app_module.next_id = 4
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_index_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_index_contains_app_name(client):
    data = client.get("/").json()
    assert data["app"] == "DevOps Demo App"


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_all_tasks(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_get_task_by_id(client):
    response = client.get("/tasks/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_task_not_found(client):
    response = client.get("/tasks/9999")
    assert response.status_code == 404


def test_create_task(client):
    response = client.post("/tasks", json={"title": "Nueva tarea de prueba"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Nueva tarea de prueba"
    assert data["done"] is False


def test_create_task_missing_title(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 422  # FastAPI validation error


def test_update_task_done(client):
    response = client.put("/tasks/1", json={"done": True})
    assert response.status_code == 200
    assert response.json()["done"] is True


def test_update_task_title(client):
    response = client.put("/tasks/1", json={"title": "Título actualizado"})
    assert response.status_code == 200
    assert response.json()["title"] == "Título actualizado"


def test_update_task_not_found(client):
    response = client.put("/tasks/9999", json={"done": True})
    assert response.status_code == 404


def test_delete_task(client):
    # Crear tarea para luego borrarla
    task_id = client.post("/tasks", json={"title": "Borrar esto"}).json()["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_delete_task_not_found(client):
    response = client.delete("/tasks/9999")
    assert response.status_code == 404


def test_docs_available(client):
    response = client.get("/docs")
    assert response.status_code == 200

import pytest
from fastapi.testclient import TestClient
import config_status_service.main as cs_mod  # импортируем модуль, где используется publish_message
from config_status_service.main import app, tasks_db

# Fake publish function that does nothing (stub)
async def fake_publish_message(message: dict):
    return

@pytest.fixture(autouse=True)
def clear_tasks():
    tasks_db.clear()

def test_create_config_task(monkeypatch):
    # Override the publish_message function in the module where it is used
    monkeypatch.setattr(cs_mod, "publish_message", fake_publish_message)

    payload = {
        "timeoutInSeconds": 14,
        "parameters": {
            "username": "admin",
            "password": "admin",
            "vlan": 534,
            "interfaces": [1, 2, 3, 4]
        }
    }
    client = TestClient(app)
    response = client.post("/api/v1/equipment/cpe/ABC123", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "taskId" in data
    task_id = data["taskId"]
    # Check that the task is stored in in-memory storage and its status is "running"
    assert task_id in tasks_db
    assert tasks_db[task_id]["status"] == "running"

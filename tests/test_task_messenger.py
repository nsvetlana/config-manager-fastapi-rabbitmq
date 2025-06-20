# tests/test_task_messenger.py
import pytest
import asyncio
from task_messenger.main import process_task
from broker import tasks_db
import httpx

# Фейковый ответ от сервиса A
class FakeResponse:
    def __init__(self, json_data):
        self._json_data = json_data
    async def json(self):
        return self._json_data

# Фейковый асинхронный клиент, который имитирует успешный вызов
class FakeAsyncClient:
    def __init__(self, *args, **kwargs):
        self.verify = kwargs.get("verify", None)
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    async def post(self, url, json):
        return FakeResponse({"code": 200, "message": "success"})

@pytest.mark.asyncio
async def test_process_task_success(monkeypatch):
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: FakeAsyncClient(**kwargs))
    task_data = {
        "task_id": "test-task",
        "equipment_id": "ABC123",
        "task_payload": {
            "timeoutInSeconds": 14,
            "parameters": {"username": "admin", "password": "admin", "interfaces": [1, 2, 3, 4]}
        }
    }
    tasks_db["test-task"] = {"status": "running", "equipment_id": "ABC123", "parameters": {}}
    await process_task(task_data)
    assert tasks_db["test-task"]["status"] == "completed"

# Фейковый клиент, имитирующий ошибку подключения
class FakeAsyncClientFailure(FakeAsyncClient):
    async def post(self, url, json):
        raise Exception("Connection error")

@pytest.mark.asyncio
async def test_process_task_failure(monkeypatch):
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: FakeAsyncClientFailure(**kwargs))
    task_data = {
        "task_id": "failed-task",
        "equipment_id": "ABC123",
        "task_payload": {
            "timeoutInSeconds": 14,
            "parameters": {"username": "admin", "password": "admin", "interfaces": [1, 2, 3, 4]}
        }
    }
    tasks_db["failed-task"] = {"status": "running", "equipment_id": "ABC123", "parameters": {}}
    await process_task(task_data)
    assert tasks_db["failed-task"]["status"] == "failed"

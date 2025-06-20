import pytest
from fastapi.testclient import TestClient
from cpe_locate_service.main import app
import time

# Отключаем реальное ожидание, чтобы тесты выполнялись быстро
@pytest.fixture(autouse=True)
def override_sleep(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda seconds: None)

def test_configure_valid():
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
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "success"

def test_invalid_device_id():
    payload = {
        "timeoutInSeconds": 14,
        "parameters": {
            "username": "admin",
            "password": "admin",
            "interfaces": [1, 2, 3, 4]
        }
    }
    client = TestClient(app)
    # Идентификатор меньше 6 символов – ожидаем 404
    response = client.post("/api/v1/equipment/cpe/abc", json=payload)
    assert response.status_code == 404

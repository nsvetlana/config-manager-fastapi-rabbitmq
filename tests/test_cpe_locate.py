import pytest
from fastapi.testclient import TestClient
from cpe_locate_service.main import app
import time

# Disable real waiting so that tests execute quickly
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
    # Identifier is less than 6 characters - expect a 404 error
    response = client.post("/api/v1/equipment/cpe/abc", json=payload)
    assert response.status_code == 404

"""
Unit tests for FastAPI Asset Management Center endpoints (Epic 1).
"""

import pytest
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


def test_api_get_providers():
    response = client.get("/api/v1/assets/providers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 10


def test_api_save_provider():
    payload = {
        "provider_id": "test_provider",
        "name": "Test LLM Provider",
        "enabled": True,
        "model": "test-v1",
        "temperature": 0.5,
        "max_tokens": 1024
    }
    response = client.post("/api/v1/assets/providers", json=payload)
    assert response.status_code == 200
    providers = response.json()
    assert any(p["provider_id"] == "test_provider" for p in providers)


def test_api_test_provider_connection():
    response = client.post("/api/v1/assets/providers/openai/test")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "connected"
    assert "latency_ms" in data


def test_api_discover_provider_models():
    response = client.get("/api/v1/assets/providers/openai/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "gpt-4o" in data["models"]


def test_api_get_agents():
    response = client.get("/api/v1/assets/agents")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 4


def test_api_create_agent():
    payload = {
        "id": "test_agent_1",
        "name": "Custom Test Agent",
        "family": "Stealth",
        "mutation_family": "Persona",
        "mode": "Single turn",
        "enabled": True
    }
    response = client.post("/api/v1/assets/agents", json=payload)
    assert response.status_code == 200
    agents = response.json()
    assert any(a["id"] == "test_agent_1" for a in agents)


def test_api_get_templates():
    response = client.get("/api/v1/assets/templates")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 9


def test_api_get_plugins():
    response = client.get("/api/v1/assets/plugins")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 7


def test_api_toggle_plugin():
    response = client.post("/api/v1/assets/plugins/hackaprompt_adapter/toggle")
    assert response.status_code == 200
    plugins = response.json()
    target = next((p for p in plugins if p["id"] == "hackaprompt_adapter"), None)
    assert target is not None

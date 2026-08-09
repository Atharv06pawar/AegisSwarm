"""
FastAPI integration unit tests for Research Benchmark Harness endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


def test_api_get_research_status():
    response = client.get("/api/v1/research")
    assert response.status_code == 200
    data = response.json()
    assert "benchmark_id" in data
    assert "status" in data
    assert data["status"] == "COMPLETED"


def test_api_post_research_run():
    payload = {
        "objective": "FastAPI Research API Test Run",
        "max_attacks_per_dataset": 2,
        "parallelism": 2
    }
    response = client.post("/api/v1/research/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert len(data["datasets"]) >= 7


def test_api_get_research_datasets():
    response = client.get("/api/v1/research/datasets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 7


def test_api_get_research_providers():
    response = client.get("/api/v1/research/providers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5


def test_api_get_research_strategies():
    response = client.get("/api/v1/research/strategies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 7


def test_api_get_research_swarm():
    response = client.get("/api/v1/research/swarm")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 4


def test_api_get_research_learning():
    response = client.get("/api/v1/research/learning")
    assert response.status_code == 200
    data = response.json()
    assert "memory_growth" in data


def test_api_get_research_telemetry():
    response = client.get("/api/v1/research/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert "events_emitted" in data


def test_api_get_research_reports():
    response = client.get("/api/v1/research/reports")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "reports" in data

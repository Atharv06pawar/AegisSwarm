"""
Unit tests for FastAPI Experiments & Benchmark Wizard endpoints (Epic 2).
"""

import pytest
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


def test_api_launch_benchmark_wizard():
    payload = {
        "objective": "FastAPI Benchmark Wizard Test Launch",
        "max_attacks_per_dataset": 2,
        "parallelism": 2
    }
    response = client.post("/api/v1/experiments/benchmark/launch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "benchmark_id" in data
    assert data["status"] == "COMPLETED"
    assert data["overall_health"] in ["PASS", "OK"]

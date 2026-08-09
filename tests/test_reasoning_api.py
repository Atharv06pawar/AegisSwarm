"""
Unit tests for FastAPI Reasoning Endpoints under /api/v1/reasoning.
"""

from fastapi.testclient import TestClient
from api.app import create_app

app = create_app()
client = TestClient(app)


def test_reasoning_api_endpoints():
    # 1. GET /api/v1/reasoning/status
    res = client.get("/api/v1/reasoning/status")
    assert res.status_code == 200
    assert "total_plans" in res.json()

    # 2. GET /api/v1/reasoning/strategies
    res = client.get("/api/v1/reasoning/strategies")
    assert res.status_code == 200
    assert len(res.json()) >= 5

    # 3. GET /api/v1/reasoning/memory
    res = client.get("/api/v1/reasoning/memory")
    assert res.status_code == 200

    # 4. GET /api/v1/reasoning/reports
    res = client.get("/api/v1/reasoning/reports")
    assert res.status_code == 200
    assert "latest_report" in res.json()

    # 5. POST /api/v1/reasoning/plan
    payload = {
        "objective": "API Integration Test Objective",
        "target_provider": "openai",
        "target_model": "gpt-4o",
        "max_candidates": 5
    }
    res = client.post("/api/v1/reasoning/plan", json=payload)
    assert res.status_code == 200
    json_data = res.json()
    assert "chosen_strategy" in json_data
    assert len(json_data["all_candidates"]) >= 5

    # 6. POST /api/v1/reasoning/reflect
    res = client.post("/api/v1/reasoning/reflect?campaign_id=cmp-api-test")
    assert res.status_code == 200
    assert "what_worked" in res.json()

    # 7. POST /api/v1/reasoning/reset
    res = client.post("/api/v1/reasoning/reset")
    assert res.status_code == 200
    assert res.json()["status"] == "reset_completed"

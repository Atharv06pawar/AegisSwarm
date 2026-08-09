"""
Unit tests for FastAPI Orchestrator Endpoints under /api/v1/orchestrator.
"""

from fastapi.testclient import TestClient
from api.app import create_app

app = create_app()
client = TestClient(app)


def test_orchestrator_api_endpoints():
    # 1. GET /api/v1/orchestrator/status
    res = client.get("/api/v1/orchestrator/status")
    assert res.status_code == 200
    assert "total_missions" in res.json()

    # 2. GET /api/v1/orchestrator/missions
    res = client.get("/api/v1/orchestrator/missions")
    assert res.status_code == 200

    # 3. GET /api/v1/orchestrator/graphs
    res = client.get("/api/v1/orchestrator/graphs")
    assert res.status_code == 200

    # 4. GET /api/v1/orchestrator/reports
    res = client.get("/api/v1/orchestrator/reports")
    assert res.status_code == 200
    assert "latest_report" in res.json()

    # 5. POST /api/v1/orchestrator/mission
    payload = {
        "objective": "API Mission Test Objective",
        "target_provider": "openai",
        "target_model": "gpt-4o",
        "budget_usd": 15.0,
        "max_attacks": 5,
        "parallelism": 2
    }
    res = client.post("/api/v1/orchestrator/mission", json=payload)
    assert res.status_code == 200
    m_data = res.json()
    assert m_data["state"] == "COMPLETED"
    mission_id = m_data["mission_id"]

    # 6. POST /api/v1/orchestrator/pause
    res = client.post(f"/api/v1/orchestrator/pause?mission_id={mission_id}")
    assert res.status_code == 200

    # 7. POST /api/v1/orchestrator/resume
    res = client.post(f"/api/v1/orchestrator/resume?mission_id={mission_id}")
    assert res.status_code == 200

    # 8. POST /api/v1/orchestrator/recover
    res = client.post(f"/api/v1/orchestrator/recover?mission_id={mission_id}")
    assert res.status_code == 200

    # 9. POST /api/v1/orchestrator/reset
    res = client.post("/api/v1/orchestrator/reset")
    assert res.status_code == 200
    assert res.json()["status"] == "reset_completed"

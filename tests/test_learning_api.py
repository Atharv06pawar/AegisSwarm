import pytest
from fastapi.testclient import TestClient


def test_learning_overview_endpoint(test_client: TestClient):
    """Test GET /api/v1/learning returns engine status and params."""
    res = test_client.get("/api/v1/learning")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "active"
    assert "statistics" in data


def test_learning_memory_and_strategies(test_client: TestClient):
    """Test GET /api/v1/learning/memory and GET /api/v1/learning/strategies."""
    m_res = test_client.get("/api/v1/learning/memory")
    assert m_res.status_code == 200
    assert isinstance(m_res.json(), list)

    s_res = test_client.get("/api/v1/learning/strategies")
    assert s_res.status_code == 200
    assert isinstance(s_res.json(), list)


def test_learning_graph_and_replays(test_client: TestClient):
    """Test GET /api/v1/learning/graph and GET /api/v1/learning/replays."""
    g_res = test_client.get("/api/v1/learning/graph")
    assert g_res.status_code == 200
    assert "nodes" in g_res.json()

    r_res = test_client.get("/api/v1/learning/replays")
    assert r_res.status_code == 200
    assert isinstance(r_res.json(), list)


def test_learning_statistics_optimize_replay_reset(test_client: TestClient):
    """Test GET /api/v1/learning/statistics, POST optimize, POST replay, POST reset."""
    stat_res = test_client.get("/api/v1/learning/statistics")
    assert stat_res.status_code == 200

    opt_res = test_client.post("/api/v1/learning/optimize")
    assert opt_res.status_code == 200

    rep_res = test_client.post("/api/v1/learning/replay?campaign_id=camp-test")
    assert rep_res.status_code == 200
    assert rep_res.json()["original_campaign_id"] == "camp-test"

    reset_res = test_client.post("/api/v1/learning/reset")
    assert reset_res.status_code == 200
    assert reset_res.json()["status"] == "reset_completed"

import pytest
from fastapi.testclient import TestClient


def test_cluster_overview_endpoint(test_client: TestClient):
    """Test GET /api/v1/cluster returns cluster snapshot state."""
    res = test_client.get("/api/v1/cluster")
    assert res.status_code == 200
    data = res.json()
    assert "total_workers" in data
    assert "online_workers" in data


def test_cluster_workers_endpoints(test_client: TestClient):
    """Test GET /api/v1/cluster/workers and GET /api/v1/cluster/workers/{id}."""
    res = test_client.get("/api/v1/cluster/workers")
    assert res.status_code == 200
    workers = res.json()
    assert len(workers) >= 1

    wid = workers[0]["worker_id"]
    get_res = test_client.get(f"/api/v1/cluster/workers/{wid}")
    assert get_res.status_code == 200
    assert get_res.json()["worker_id"] == wid


def test_cluster_health_and_statistics(test_client: TestClient):
    """Test GET /api/v1/cluster/health and GET /api/v1/cluster/statistics."""
    h_res = test_client.get("/api/v1/cluster/health")
    assert h_res.status_code == 200
    assert "worker_health" in h_res.json()

    s_res = test_client.get("/api/v1/cluster/statistics")
    assert s_res.status_code == 200
    assert "capacity" in s_res.json()


def test_cluster_register_shutdown_rebalance(test_client: TestClient):
    """Test POST /api/v1/cluster/register, POST /api/v1/cluster/shutdown, POST /api/v1/cluster/rebalance."""
    reg_res = test_client.post("/api/v1/cluster/register?hostname=node-api-test")
    assert reg_res.status_code == 201
    worker_data = reg_res.json()
    wid = worker_data["worker_id"]

    reb_res = test_client.post("/api/v1/cluster/rebalance?target_count=3")
    assert reb_res.status_code == 200
    assert reb_res.json()["target_count"] == 3

    shut_res = test_client.post(f"/api/v1/cluster/shutdown?worker_id={wid}")
    assert shut_res.status_code == 200
    assert shut_res.json()["status"] == "shutdown_completed"

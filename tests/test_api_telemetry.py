import pytest
from fastapi.testclient import TestClient


def test_telemetry_overview_endpoint(test_client: TestClient):
    """Test GET /api/v1/telemetry returns overview dashboard data."""
    res = test_client.get("/api/v1/telemetry")
    assert res.status_code == 200
    data = res.json()
    assert data["system_status"] == "healthy"
    assert "requests_per_sec" in data


def test_telemetry_events_endpoint(test_client: TestClient):
    """Test GET /api/v1/telemetry/events returns event list."""
    res = test_client.get("/api/v1/telemetry/events")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_telemetry_metrics_endpoint(test_client: TestClient):
    """Test GET /api/v1/telemetry/metrics returns metrics summary."""
    res = test_client.get("/api/v1/telemetry/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "counters" in data
    assert "rates" in data


def test_telemetry_traces_endpoint(test_client: TestClient):
    """Test GET /api/v1/telemetry/traces returns traces list."""
    res = test_client.get("/api/v1/telemetry/traces")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_telemetry_dashboard_endpoint(test_client: TestClient):
    """Test GET /api/v1/telemetry/dashboard returns dashboard data."""
    res = test_client.get("/api/v1/telemetry/dashboard")
    assert res.status_code == 200
    assert "provider_status" in res.json()


def test_telemetry_providers_endpoint(test_client: TestClient):
    """Test GET /api/v1/telemetry/providers returns provider status."""
    res = test_client.get("/api/v1/telemetry/providers")
    assert res.status_code == 200
    data = res.json()
    assert "providers" in data


def test_telemetry_campaigns_endpoint(test_client: TestClient):
    """Test GET /api/v1/telemetry/campaigns returns campaign status."""
    res = test_client.get("/api/v1/telemetry/campaigns")
    assert res.status_code == 200
    data = res.json()
    assert "active_campaigns" in data


def test_telemetry_reset_endpoint(test_client: TestClient):
    """Test POST /api/v1/telemetry/reset clears in-memory state."""
    res = test_client.post("/api/v1/telemetry/reset")
    assert res.status_code == 200
    assert res.json()["status"] == "reset_completed"

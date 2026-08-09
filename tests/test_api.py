import pytest
from fastapi.testclient import TestClient

def test_health_endpoint(test_client: TestClient):
    """Test GET /health returns HTTP 200 and healthy status."""
    res = test_client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_version_endpoint(test_client: TestClient):
    """Test GET /version returns system metadata."""
    res = test_client.get("/version")
    assert res.status_code == 200
    data = res.json()
    assert data["version"] == "2.0.0"

def test_plugins_endpoints(test_client: TestClient):
    """Test GET /api/v1/plugins and POST /api/v1/plugins/discover."""
    res = test_client.get("/api/v1/plugins")
    assert res.status_code == 200
    data = res.json()
    assert "total_count" in data
    assert isinstance(data["plugins"], list)

    disc_res = test_client.post("/api/v1/plugins/discover")
    assert disc_res.status_code == 200

def test_dashboard_endpoint(test_client: TestClient):
    """Test GET /api/v1/dashboard telemetry response structure."""
    res = test_client.get("/api/v1/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "total_records" in data
    assert "total_datasets" in data
    assert "active_plugins" in data

def test_corpus_endpoints(test_client: TestClient):
    """Test GET /api/v1/corpus, datasets, statistics, coverage, quality, verification."""
    res = test_client.get("/api/v1/corpus")
    assert res.status_code == 200

    ds_res = test_client.get("/api/v1/corpus/datasets")
    assert ds_res.status_code == 200
    assert isinstance(ds_res.json(), list)

    stats_res = test_client.get("/api/v1/corpus/statistics")
    assert stats_res.status_code == 200

    cov_res = test_client.get("/api/v1/corpus/coverage")
    assert cov_res.status_code == 200

    qual_res = test_client.get("/api/v1/corpus/quality")
    assert qual_res.status_code == 200

    ver_res = test_client.get("/api/v1/corpus/verification")
    assert ver_res.status_code == 200

def test_search_endpoint(test_client: TestClient):
    """Test POST /api/v1/search query validation and results."""
    res = test_client.post("/api/v1/search", json={"query": "test", "limit": 10})
    assert res.status_code == 200
    data = res.json()
    assert "total_matches" in data
    assert "results" in data

def test_reports_endpoints(test_client: TestClient):
    """Test GET /api/v1/reports and POST /api/v1/reports/generate."""
    res = test_client.get("/api/v1/reports")
    assert res.status_code == 200

    gen_res = test_client.post("/api/v1/reports/generate")
    assert gen_res.status_code == 200
    assert "markdown_path" in gen_res.json()

def test_ingest_and_jobs_endpoints(test_client: TestClient):
    """Test POST /api/v1/ingest submission and GET /api/v1/jobs status."""
    ingest_res = test_client.post(
        "/api/v1/ingest",
        json={"datasets": ["hackaprompt"], "dry_run": True, "batch_size": 100}
    )
    assert ingest_res.status_code == 202
    job_id = ingest_res.json()["job_id"]
    assert job_id.startswith("job_")

    job_res = test_client.get(f"/api/v1/jobs/{job_id}")
    assert job_res.status_code == 200
    assert job_res.json()["job_id"] == job_id

    jobs_list = test_client.get("/api/v1/jobs")
    assert jobs_list.status_code == 200
    assert jobs_list.json()["total_jobs"] >= 1

def test_invalid_dataset_ingest_validation(test_client: TestClient):
    """Test POST /api/v1/ingest with invalid dataset ID returns HTTP 400."""
    res = test_client.post("/api/v1/ingest", json={"datasets": ["invalid_dataset_123"]})
    assert res.status_code == 400
    data = res.json()
    assert "detail" in data

def test_campaigns_api_endpoints(test_client: TestClient):
    """Test POST /api/v1/campaigns, GET /campaigns, GET /campaigns/{id}, start, pause, resume, cancel, metrics, report."""
    config_payload = {
        "name": "API Test Campaign",
        "objective": {"name": "Test Obj", "description": "Desc"},
        "targets": [{"provider": "openai", "model": "gpt-4o", "max_concurrency": 2}],
        "selected_datasets": ["jailbreakbench"],
        "swarm_agents": ["jailbreak"],
        "maximum_attacks": 10,
        "parallel_workers": 2,
        "budget": {"max_cost_usd": 10.0}
    }

    create_res = test_client.post("/api/v1/campaigns", json=config_payload)
    assert create_res.status_code == 201
    config = create_res.json()
    cid = config["campaign_id"]

    list_res = test_client.get("/api/v1/campaigns")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    get_res = test_client.get(f"/api/v1/campaigns/{cid}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "API Test Campaign"

    start_res = test_client.post(f"/api/v1/campaigns/{cid}/start")
    assert start_res.status_code == 200

    pause_res = test_client.post(f"/api/v1/campaigns/{cid}/pause")
    assert pause_res.status_code == 200

    resume_res = test_client.post(f"/api/v1/campaigns/{cid}/resume")
    assert resume_res.status_code == 200

    cancel_res = test_client.post(f"/api/v1/campaigns/{cid}/cancel")
    assert cancel_res.status_code == 200

    metrics_res = test_client.get(f"/api/v1/campaigns/{cid}/metrics")
    assert metrics_res.status_code == 200

    report_res = test_client.get(f"/api/v1/campaigns/{cid}/report?format=markdown")
    assert report_res.status_code == 200
    assert "Campaign Audit Report: API Test Campaign" in report_res.text

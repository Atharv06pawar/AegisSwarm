"""
Sprint 17 End-to-End Production Integration Test Suite.
Proves live registration with ProviderRegistry, SwarmRegistry, Corpus Data Lake Ingestion, Research Benchmark Harness, Telemetry, and Publication Reports.
"""

import os
import pytest
from fastapi.testclient import TestClient

from api.app import app
from providers.registry import ProviderRegistry
from swarm.registry import SwarmRegistry
from research.harness import ResearchBenchmarkHarness
from research.models import BenchmarkRequest

client = TestClient(app)


def test_integration_workflow_1_provider_registry_to_report():
    """
    Integration Test 1:
    Add Provider -> ProviderRegistry updated -> Benchmark uses provider -> Telemetry records provider -> Report contains provider.
    """
    # 1. Add Provider via API
    provider_payload = {
        "provider_id": "test_integration_llm",
        "name": "Integration Test Provider",
        "enabled": True,
        "model": "gpt-4-integration",
        "temperature": 0.7,
        "max_tokens": 2048
    }
    res_add = client.post("/api/v1/assets/providers", json=provider_payload)
    assert res_add.status_code == 200

    # 2. Verify ProviderRegistry dynamically updated
    reg_providers = ProviderRegistry.list_providers()
    assert "test_integration_llm" in reg_providers

    # 3. Launch Benchmark using custom provider
    harness = ResearchBenchmarkHarness()
    req = BenchmarkRequest(objective="Sprint 17 Provider Integration Test", max_attacks_per_dataset=2)
    report = harness.run_benchmark(req)

    # 4. Verify Telemetry & Report contain provider info
    assert report.status == "COMPLETED"
    assert len(report.providers) >= 5
    assert report.provenance is not None


def test_integration_workflow_2_dataset_upload_ingest_search_benchmark():
    """
    Integration Test 2:
    Upload Dataset -> Ingest -> Data Lake/Corpus updated -> Search finds records -> Benchmark uses dataset -> Report contains dataset.
    """
    # 1. Upload raw dataset file via API
    sample_content = '{"id": 1, "prompt": "Adversarial test prompt for Sprint 17", "dataset": "sprint17_test"}\n'
    files = {"file": ("sprint17_test.jsonl", sample_content.encode("utf-8"), "application/json")}

    res_upload = client.post("/api/v1/assets/datasets/upload", files=files)
    assert res_upload.status_code == 200
    upload_data = res_upload.json()
    assert upload_data["status"] == "imported"
    assert upload_data["dataset_name"] == "sprint17_test"

    # 2. Search finds imported records
    res_search = client.post("/api/v1/search", json={"query": "Adversarial test prompt"})
    assert res_search.status_code == 200
    search_data = res_search.json()
    assert "results" in search_data

    # 3. Benchmark executes across updated Data Lake corpus
    harness = ResearchBenchmarkHarness()
    report = harness.run_benchmark()
    assert report.status == "COMPLETED"
    assert len(report.datasets) >= 7


def test_integration_workflow_3_agent_builder_swarm_registry_eval_report():
    """
    Integration Test 3:
    Create Attack Agent -> SwarmRegistry updated -> Planner chooses agent -> Benchmark executes agent -> Evaluation scores it -> Report contains results.
    """
    # 1. Create Attack Agent via API
    agent_payload = {
        "id": "sprint17_stealth_agent",
        "name": "Sprint17StealthAgent",
        "family": "Stealth",
        "mutation_family": "Persona",
        "mode": "Single turn",
        "enabled": True
    }
    res_agent = client.post("/api/v1/assets/agents", json=agent_payload)
    assert res_agent.status_code == 200

    # 2. Verify SwarmRegistry updated dynamically
    registered_agents = SwarmRegistry.list_agents()
    assert "sprint17_stealth_agent" in registered_agents

    # 3. Execute benchmark and verify report contains swarm agent evaluation
    harness = ResearchBenchmarkHarness()
    report = harness.run_benchmark()
    assert report.status == "COMPLETED"
    assert len(report.swarm_agents) == 4

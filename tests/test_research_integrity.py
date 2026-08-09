"""
Unit tests for Dataset Integrity, Quality Gates, Statistics, Repeatability & Publication Checklist (Sprint 16.3).
"""

import pytest
from research.models import BenchmarkReport, BenchmarkRequest, DatasetBenchmarkMetric
from research.integrity import DatasetIntegrityValidator, BenchmarkIntegrityValidator
from research.statistics import StatisticalValidator
from research.repeatability import RepeatabilityEngine
from research.checklist import PublicationChecklistEvaluator
from research.harness import ResearchBenchmarkHarness


def test_dataset_integrity_validator(tmp_path):
    validator = DatasetIntegrityValidator(reports_dir=str(tmp_path))
    report = validator.validate_all_datasets()
    assert report.total_datasets == 7
    assert len(report.datasets) == 7
    for d in report.datasets:
        assert d.checksum_sha256.startswith("sha256:")


def test_benchmark_integrity_validator():
    validator = BenchmarkIntegrityValidator()

    # Valid report
    valid_report = BenchmarkReport(
        benchmark_id="bench_ok",
        attacks_executed=10,
        successful_attacks=8,
        failed_attacks=2,
        average_latency_ms=45.0,
        p50_latency_ms=40.0,
        p95_latency_ms=50.0,
        evaluation_score=0.85,
        average_confidence=0.90,
        refusal_rate=0.02,
        datasets=[
            DatasetBenchmarkMetric(dataset_id=ds, records=10, executed=10)
            for ds in DatasetIntegrityValidator.SUPPORTED_DATASETS
        ]
    )
    status, reasons = validator.validate_benchmark_integrity(valid_report)
    assert status == "PASS"

    # Invalid report (non-positive latency)
    invalid_report = valid_report.model_copy()
    invalid_report.average_latency_ms = -5.0
    status, reasons = validator.validate_benchmark_integrity(invalid_report)
    assert status in ["DEGRADED", "FAIL"]


def test_statistical_validator():
    validator = StatisticalValidator()
    summary = validator.calculate_summary([10.0, 20.0, 30.0, 40.0, 50.0])
    assert summary.mean == 30.0
    assert summary.median == 30.0
    assert summary.p50 == 30.0
    assert summary.std_dev > 0.0
    assert summary.ci_95_lower < summary.mean < summary.ci_95_upper


def test_repeatability_engine(tmp_path):
    engine = RepeatabilityEngine(reports_dir=str(tmp_path))
    report = BenchmarkReport(benchmark_id="bench_rep_1", evaluation_score=0.92, average_latency_ms=45.0)
    rep_report = engine.evaluate_repeatability(report)
    assert rep_report.total_runs >= 1
    assert rep_report.ranking_stability >= 0.8


def test_publication_checklist_evaluator(tmp_path):
    evaluator = PublicationChecklistEvaluator(reports_dir=str(tmp_path), provenance_dir=str(tmp_path))
    harness = ResearchBenchmarkHarness()
    report = harness.run_benchmark()
    checklist = evaluator.evaluate_checklist(report)
    assert checklist.benchmark_completed is True


def test_research_api_sprint_16_3_endpoints():
    from fastapi.testclient import TestClient
    from api.app import app

    client = TestClient(app)

    r_prov = client.get("/api/v1/research/provenance")
    assert r_prov.status_code == 200
    assert "git_commit_hash" in r_prov.json()

    r_repro = client.get("/api/v1/research/reproducibility")
    assert r_repro.status_code == 200
    assert "manifest_id" in r_repro.json()

    r_integ = client.get("/api/v1/research/integrity")
    assert r_integ.status_code == 200
    assert "total_datasets" in r_integ.json()

    r_stats = client.get("/api/v1/research/statistics")
    assert r_stats.status_code == 200
    assert "latency_ms" in r_stats.json()

    r_repeat = client.get("/api/v1/research/repeatability")
    assert r_repeat.status_code == 200
    assert "ranking_stability" in r_repeat.json()

    r_artifacts = client.get("/api/v1/research/artifacts")
    assert r_artifacts.status_code == 200
    assert "artifact_hashes" in r_artifacts.json()

    r_check = client.get("/api/v1/research/checklist")
    assert r_check.status_code == 200
    assert "publication_ready" in r_check.json()

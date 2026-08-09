"""
Unit tests for AegisSwarm Production Research Benchmark Harness & Report Generator (Sprint 16.3).
"""

import pytest
from research.models import BenchmarkRequest, BenchmarkReport
from research.harness import ResearchBenchmarkHarness
from research.datasets import DatasetBenchmarkEvaluator
from research.providers import ProviderBenchmarkEvaluator
from research.strategies import StrategyBenchmarkEvaluator
from research.swarm import SwarmAgentBenchmarkEvaluator
from research.learning import LearningBenchmarkEvaluator
from research.telemetry import TelemetryBenchmarkEvaluator
from research.reports import ResearchReportGenerator
from research.persistence import ResearchPersistence


def test_dataset_benchmark_evaluator():
    evaluator = DatasetBenchmarkEvaluator()
    metrics = evaluator.evaluate_datasets(target_provider="openai")
    assert len(metrics) >= 7
    for m in metrics:
        assert m.dataset_id in evaluator.SUPPORTED_DATASETS
        assert m.executed > 0
        assert m.success_rate >= 0.0


def test_provider_benchmark_evaluator():
    evaluator = ProviderBenchmarkEvaluator()
    metrics = evaluator.evaluate_providers(attack_sample_count=5)
    assert len(metrics) == 5
    ranks = [m.rank for m in metrics]
    assert sorted(ranks) == [1, 2, 3, 4, 5]


def test_strategy_benchmark_evaluator():
    evaluator = StrategyBenchmarkEvaluator()
    metrics = evaluator.evaluate_strategies(sample_count=5)
    assert len(metrics) >= 7
    for m in metrics:
        assert m.strategy_family in [s["family"] for s in evaluator.STRATEGY_FAMILIES]


def test_swarm_agent_benchmark_evaluator():
    evaluator = SwarmAgentBenchmarkEvaluator()
    metrics = evaluator.evaluate_swarm_agents(sample_count=5)
    assert len(metrics) == 4
    for m in metrics:
        assert m.attacks >= 5


def test_learning_benchmark_evaluator():
    evaluator = LearningBenchmarkEvaluator()
    m = evaluator.evaluate_learning()
    assert m.strategy_updates >= 0
    assert m.graph_growth >= 0


def test_telemetry_benchmark_evaluator():
    evaluator = TelemetryBenchmarkEvaluator()
    m = evaluator.evaluate_telemetry()
    assert m.events_emitted >= 0
    assert m.spans_created >= 0


def test_research_benchmark_harness_run():
    harness = ResearchBenchmarkHarness()
    req = BenchmarkRequest(max_attacks_per_dataset=2, parallelism=2)
    report = harness.run_benchmark(req)

    assert isinstance(report, BenchmarkReport)
    assert report.status == "COMPLETED"
    assert report.overall_health in ["PASS", "OK"]
    assert len(report.datasets) >= 7
    assert len(report.providers) == 5
    assert len(report.strategies) >= 7
    assert len(report.swarm_agents) == 4


def test_research_report_generator(tmp_path):
    generator = ResearchReportGenerator(output_dir=str(tmp_path))
    harness = ResearchBenchmarkHarness()
    report = harness.run_benchmark()

    written = generator.generate_all_reports(report)
    assert len(written) >= 9
    assert "benchmark.json" in written
    assert "benchmark.md" in written
    assert "provider_report.md" in written
    assert "dataset_report.md" in written
    assert "strategy_report.md" in written
    assert "swarm_report.md" in written
    assert "learning_report.md" in written
    assert "telemetry_report.md" in written
    assert "research_summary.md" in written
    assert "provenance_report.md" in written
    assert "integrity_report.md" in written
    assert "repeatability_report.md" in written
    assert "statistics_report.md" in written
    assert "artifact_hash_report.md" in written
    assert "reproducibility_report.md" in written
    assert "publication_checklist.md" in written


def test_research_persistence(tmp_path):
    persistence = ResearchPersistence(reports_dir=str(tmp_path))
    harness = ResearchBenchmarkHarness()
    report = harness.run_benchmark()

    saved_path = persistence.save_report(report)
    assert saved_path.endswith("benchmark.json")

    loaded = persistence.get_latest_report()
    assert loaded is not None
    assert loaded.benchmark_id == report.benchmark_id
